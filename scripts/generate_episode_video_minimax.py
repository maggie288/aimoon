#!/usr/bin/env python3
"""
将单集对话拆成镜头并调用 MiniMax 文生视频接口生成镜头 MP4。

功能：
- 读取 backend/data/conversations/{date}.json
- 生成 shot_plan.json（每个镜头包含角色、对白、画面提示词、目标时长）
- 调 MiniMax 视频接口提交任务、轮询、下载片段到 backend/media/video_work/{date}/clips
- 失败镜头可回退为静态占位视频（可选）

说明：
- 由于各账号可用的视频模型/字段可能不同，脚本提供环境变量覆盖端点与关键参数。
- 默认端点采用常见约定，如不匹配请在 backend/.env 中设置 MINIMAX_VIDEO_* 覆盖。
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Optional

import requests

REPO = Path(__file__).resolve().parent.parent
BACKEND = REPO / "backend"
DATA_DIR = BACKEND / "data" / "conversations"
IMAGE_DIR = BACKEND / "media" / "images"
WORK_ROOT = BACKEND / "media" / "video_work"


ROLE_PROFILE = {
    "elena": "female science fiction writer, calm and poetic, Chinese, in lunar base command cabin",
    "chenwei": "male physicist, precise and composed, Chinese, in lunar base operations room",
    "alice": "female computer scientist, analytical and fast-paced, Chinese, in lunar base console area",
    "oldtom": "male veteran mechanic, rough but warm, Chinese, in lunar base engineering bay",
}


def _load_env() -> None:
    env_file = BACKEND / ".env"
    if not env_file.exists():
        return
    try:
        from dotenv import load_dotenv

        load_dotenv(env_file)
    except Exception:
        # python-dotenv 非强依赖；仅在已安装时加载
        pass


def _norm_text(text: str) -> str:
    return (
        (text or "")
        .replace("₂", "2")
        .replace("₁", "1")
        .replace("₀", "0")
        .replace("\n", " ")
        .strip()
    )


@dataclass
class Shot:
    shot_id: int
    role_id: str
    text: str
    media_id: Optional[str]
    duration_sec: int
    prompt: str
    source_msg_index: int


def _extract_paragraphs(msg: dict) -> list[str]:
    out: list[str] = []
    for b in msg.get("content_blocks") or []:
        if b.get("type") == "paragraph" and b.get("content"):
            out.append(_norm_text(str(b["content"])))
    return [t for t in out if t]


def _extract_first_media_id(msg: dict) -> Optional[str]:
    for b in msg.get("content_blocks") or []:
        if b.get("type") == "image" and b.get("media_id"):
            return str(b.get("media_id"))
    return None


def _build_prompt(role_id: str, text: str, topic_title: str, media_hint: Optional[str]) -> str:
    role = ROLE_PROFILE.get(role_id, "Chinese lunar crew member, realistic cinematic style")
    hint = f"Reference visual theme: {media_hint}." if media_hint else ""
    short_line = text[:120]
    return (
        "Cinematic realistic lunar base scene, 24fps, physically plausible lighting, high detail. "
        f"Episode theme: {topic_title}. Character: {role}. "
        f"Dialogue context: {short_line}. {hint} "
        "Shot should be stable and coherent, no text overlay, no subtitles, no watermark."
    ).strip()


def _estimate_sec(text: str, min_sec: int = 8, max_sec: int = 20) -> int:
    # 中文口播约 3.6~4.2 字/秒，取 4.0 估算
    sec = int(round(max(1, len(text)) / 4.0))
    return max(min_sec, min(max_sec, sec))


def build_shot_plan(
    conv: dict, target_sec: int = 1800, max_chars_per_shot: int = 180
) -> list[Shot]:
    topic = str(conv.get("topic_title") or "Lunar Survival")
    shots: list[Shot] = []
    acc = 0
    shot_id = 0
    for i, msg in enumerate(conv.get("messages") or []):
        role_id = str(msg.get("role_id") or "alice")
        media_id = _extract_first_media_id(msg)
        paras = _extract_paragraphs(msg)
        if not paras:
            continue

        # 长段按字符切块，避免单镜头过长
        for p in paras:
            text = p
            while text:
                chunk = text[:max_chars_per_shot]
                text = text[max_chars_per_shot:]
                sec = _estimate_sec(chunk)
                prompt = _build_prompt(role_id, chunk, topic, media_id)
                shots.append(
                    Shot(
                        shot_id=shot_id,
                        role_id=role_id,
                        text=chunk,
                        media_id=media_id,
                        duration_sec=sec,
                        prompt=prompt,
                        source_msg_index=i,
                    )
                )
                shot_id += 1
                acc += sec
                if acc >= target_sec:
                    return shots
    return shots


def _pick(obj: dict, paths: list[list[str]]) -> Any:
    for path in paths:
        cur: Any = obj
        ok = True
        for key in path:
            if not isinstance(cur, dict) or key not in cur:
                ok = False
                break
            cur = cur[key]
        if ok and cur is not None:
            return cur
    return None


class MiniMaxVideoClient:
    def __init__(self) -> None:
        self.api_key = os.environ.get("MINIMAX_API_KEY", "").strip()
        self.group_id = os.environ.get("MINIMAX_GROUP_ID", "").strip()
        base = (
            os.environ.get("MINIMAX_VIDEO_BASE")
            or os.environ.get("MINIMAX_API_BASE")
            or "https://api.minimaxi.com"
        )
        self.base = base.rstrip("/")
        self.model = os.environ.get("MINIMAX_VIDEO_MODEL", "video-01")
        self.submit_ep = os.environ.get("MINIMAX_VIDEO_SUBMIT_ENDPOINT", "/v1/video_generation")
        self.query_ep = os.environ.get("MINIMAX_VIDEO_QUERY_ENDPOINT", "/v1/query/video_generation")
        self.timeout = int(os.environ.get("MINIMAX_VIDEO_TIMEOUT", "60"))

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def _submit_url(self) -> str:
        url = f"{self.base}{self.submit_ep}"
        if self.group_id and "GroupId=" not in url:
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}GroupId={self.group_id}"
        return url

    def _query_url(self) -> str:
        url = f"{self.base}{self.query_ep}"
        if self.group_id and "GroupId=" not in url:
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}GroupId={self.group_id}"
        return url

    def submit(self, prompt: str, duration_sec: int = 12) -> tuple[Optional[str], Optional[str], dict]:
        payload = {
            "model": self.model,
            "prompt": prompt[:1800],
            "duration": duration_sec,
            "aspect_ratio": "16:9",
            "response_format": "url",
        }
        r = requests.post(
            self._submit_url(), headers=self._headers(), json=payload, timeout=self.timeout
        )
        if r.status_code != 200:
            return None, f"submit http {r.status_code}: {r.text[:300]}", {}
        body = r.json()

        # 某些实现可能同步返回视频 URL
        video_url = _pick(
            body,
            [
                ["video_url"],
                ["file_url"],
                ["data", "video_url"],
                ["data", "file_url"],
                ["data", "output", "video_url"],
            ],
        )
        if isinstance(video_url, str) and video_url.startswith("http"):
            return "__SYNC__", None, body

        task_id = _pick(
            body,
            [
                ["task_id"],
                ["taskId"],
                ["id"],
                ["data", "task_id"],
                ["data", "taskId"],
                ["data", "id"],
            ],
        )
        if not isinstance(task_id, str):
            return None, f"missing task_id in response: {json.dumps(body)[:300]}", body
        return task_id, None, body

    def query(self, task_id: str) -> tuple[str, Optional[str], dict]:
        # 先尝试 GET + params
        params = {"task_id": task_id}
        r = requests.get(
            self._query_url(), headers=self._headers(), params=params, timeout=self.timeout
        )
        if r.status_code != 200:
            # 回退 POST
            r = requests.post(
                self._query_url(),
                headers=self._headers(),
                json={"task_id": task_id},
                timeout=self.timeout,
            )
        if r.status_code != 200:
            return "failed", None, {"error": f"query http {r.status_code}: {r.text[:300]}"}
        body = r.json()

        raw_status = str(
            _pick(body, [["status"], ["state"], ["task_status"], ["data", "status"], ["data", "state"]])
            or ""
        ).lower()
        video_url = _pick(
            body,
            [
                ["video_url"],
                ["file_url"],
                ["data", "video_url"],
                ["data", "file_url"],
                ["data", "output", "video_url"],
            ],
        )

        if isinstance(video_url, str) and video_url.startswith("http"):
            return "succeeded", video_url, body
        if raw_status in {"success", "succeeded", "completed", "done", "finished"}:
            return "succeeded", None, body
        if raw_status in {"failed", "error", "cancelled", "canceled"}:
            return "failed", None, body
        return "running", None, body

    @staticmethod
    def download(url: str, out_path: Path) -> bool:
        try:
            with requests.get(url, stream=True, timeout=120) as r:
                if r.status_code != 200:
                    return False
                out_path.parent.mkdir(parents=True, exist_ok=True)
                with open(out_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 128):
                        if chunk:
                            f.write(chunk)
            return out_path.exists() and out_path.stat().st_size > 0
        except Exception:
            return False


def _make_placeholder_clip(image_path: Optional[Path], out_path: Path, duration_sec: int) -> bool:
    src = image_path if image_path and image_path.exists() else None
    if src is None:
        # 无图则生成纯色背景
        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=black:s=1280x720:r=24",
            "-t",
            str(max(1, duration_sec)),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(out_path),
        ]
    else:
        cmd = [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(src),
            "-t",
            str(max(1, duration_sec)),
            "-vf",
            "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2",
            "-r",
            "24",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(out_path),
        ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0 and out_path.exists() and out_path.stat().st_size > 0


def _media_png(media_id: Optional[str]) -> Optional[Path]:
    if not media_id:
        return None
    for ext in (".png", ".jpg", ".jpeg", ".webp", ".svg"):
        p = IMAGE_DIR / f"{media_id}{ext}"
        if p.exists():
            return p
    return None


def main() -> int:
    _load_env()
    ap = argparse.ArgumentParser(description="Generate video clips for one episode via MiniMax video API.")
    ap.add_argument("date", help="Episode date, e.g. 2026-03-05")
    ap.add_argument("--target-seconds", type=int, default=1800, help="Target total shot duration")
    ap.add_argument("--max-shots", type=int, default=0, help="Limit number of shots (0 means unlimited)")
    ap.add_argument("--poll-interval", type=int, default=8, help="Seconds between task polling")
    ap.add_argument("--max-poll", type=int, default=120, help="Max polls per task")
    ap.add_argument("--force", action="store_true", help="Regenerate clips even if existing")
    ap.add_argument(
        "--fallback-placeholder",
        action="store_true",
        help="When API generation fails, fallback to static placeholder clips",
    )
    args = ap.parse_args()

    conv_path = DATA_DIR / f"{args.date}.json"
    if not conv_path.exists():
        print(f"Conversation not found: {conv_path}", file=sys.stderr)
        return 1
    conv = json.loads(conv_path.read_text(encoding="utf-8"))
    shots = build_shot_plan(conv, target_sec=args.target_seconds)
    if not shots:
        print("No shot generated from conversation", file=sys.stderr)
        return 1
    gen_shots = shots[: args.max_shots] if args.max_shots > 0 else shots

    work_dir = WORK_ROOT / args.date
    clips_dir = work_dir / "clips"
    work_dir.mkdir(parents=True, exist_ok=True)
    clips_dir.mkdir(parents=True, exist_ok=True)

    plan_path = work_dir / "shot_plan.json"
    plan_path.write_text(
        json.dumps(
            {
                "date": args.date,
                "topic_title": conv.get("topic_title"),
                "target_seconds": args.target_seconds,
                "shots": [asdict(s) for s in shots],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"[plan] {plan_path} ({len(shots)} shots)")

    client = MiniMaxVideoClient()
    if not client.api_key:
        print("MINIMAX_API_KEY not set", file=sys.stderr)
        return 1

    for shot in gen_shots:
        clip_path = clips_dir / f"shot_{shot.shot_id:04d}.mp4"
        if clip_path.exists() and clip_path.stat().st_size > 0 and not args.force:
            print(f"[skip] shot {shot.shot_id:04d}")
            continue

        print(f"[gen] shot {shot.shot_id:04d} ({shot.duration_sec}s)")
        task_id, err, body = client.submit(shot.prompt, duration_sec=shot.duration_sec)
        if err:
            print(f"  submit failed: {err}", file=sys.stderr)
            if args.fallback_placeholder:
                img = _media_png(shot.media_id)
                ok = _make_placeholder_clip(img, clip_path, shot.duration_sec)
                print(f"  placeholder: {'ok' if ok else 'failed'}")
                continue
            return 2

        # 同步返回
        if task_id == "__SYNC__":
            url = _pick(
                body,
                [
                    ["video_url"],
                    ["file_url"],
                    ["data", "video_url"],
                    ["data", "file_url"],
                    ["data", "output", "video_url"],
                ],
            )
            ok = isinstance(url, str) and client.download(url, clip_path)
            print(f"  sync download: {'ok' if ok else 'failed'}")
            if not ok and args.fallback_placeholder:
                img = _media_png(shot.media_id)
                _make_placeholder_clip(img, clip_path, shot.duration_sec)
            continue

        video_url: Optional[str] = None
        state = "running"
        last_body: dict = {}
        for _ in range(args.max_poll):
            state, maybe_url, last_body = client.query(task_id)
            if maybe_url:
                video_url = maybe_url
            if state in {"succeeded", "failed"}:
                break
            time.sleep(max(1, args.poll_interval))

        if state != "succeeded":
            print(f"  task failed: {json.dumps(last_body)[:400]}", file=sys.stderr)
            if args.fallback_placeholder:
                img = _media_png(shot.media_id)
                ok = _make_placeholder_clip(img, clip_path, shot.duration_sec)
                print(f"  placeholder: {'ok' if ok else 'failed'}")
                continue
            return 3

        if not video_url:
            video_url = _pick(
                last_body,
                [
                    ["video_url"],
                    ["file_url"],
                    ["data", "video_url"],
                    ["data", "file_url"],
                    ["data", "output", "video_url"],
                ],
            )
        if not isinstance(video_url, str) or not video_url.startswith("http"):
            print(f"  missing video_url in final response: {json.dumps(last_body)[:400]}", file=sys.stderr)
            if args.fallback_placeholder:
                img = _media_png(shot.media_id)
                ok = _make_placeholder_clip(img, clip_path, shot.duration_sec)
                print(f"  placeholder: {'ok' if ok else 'failed'}")
                continue
            return 4

        ok = client.download(video_url, clip_path)
        print(f"  download: {'ok' if ok else 'failed'}")
        if not ok and args.fallback_placeholder:
            img = _media_png(shot.media_id)
            _make_placeholder_clip(img, clip_path, shot.duration_sec)

    print(f"Done: {clips_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
