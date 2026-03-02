#!/usr/bin/env python3
"""
按镜头清单将文生视频片段 + 四角色对白合成为 30 分钟单集视频。

输入：
- backend/media/video_work/{date}/shot_plan.json
- backend/media/video_work/{date}/clips/shot_XXXX.mp4

输出：
- backend/media/episodes/{date}_30min.mp4
- backend/media/video_work/{date}/episode.srt
"""
from __future__ import annotations

import argparse
import asyncio
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
BACKEND = REPO / "backend"
WORK_ROOT = BACKEND / "media" / "video_work"
EPISODE_DIR = BACKEND / "media" / "episodes"
IMAGE_DIR = BACKEND / "media" / "images"

VOICE_CONFIG = {
    "chenwei": {"voice": "zh-CN-YunyangNeural", "rate": "-2%", "pitch": "+0Hz"},
    "alice": {"voice": "zh-CN-XiaoxiaoNeural", "rate": "+3%", "pitch": "+1Hz"},
    "oldtom": {"voice": "zh-CN-YunxiNeural", "rate": "-4%", "pitch": "-2Hz"},
    "elena": {"voice": "zh-CN-XiaoyiNeural", "rate": "+0%", "pitch": "+0Hz"},
}


def _norm_tts_text(text: str) -> str:
    return (
        (text or "")
        .replace("₂", "2")
        .replace("₁", "1")
        .replace("₀", "0")
        .replace("\n", " ")
        .strip()
    )


async def _tts_one(text: str, role_id: str, out_path: Path) -> bool:
    import edge_tts

    cfg = VOICE_CONFIG.get(role_id, VOICE_CONFIG["alice"])
    text = _norm_tts_text(text)[:5000]
    for _ in range(3):
        try:
            comm = edge_tts.Communicate(text, cfg["voice"], rate=cfg["rate"], pitch=cfg["pitch"])
            await comm.save(str(out_path))
            if out_path.exists() and out_path.stat().st_size > 0:
                return True
        except Exception:
            await asyncio.sleep(1.0)
    return False


def _probe_duration_sec(path: Path, fallback: float = 8.0) -> float:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return fallback
    try:
        return float(r.stdout.strip())
    except Exception:
        return fallback


def _format_srt_time(sec: float) -> str:
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int(round((sec - math.floor(sec)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _pick_fallback_image(media_id: str | None) -> Path | None:
    if media_id:
        for ext in (".png", ".jpg", ".jpeg", ".webp", ".svg"):
            p = IMAGE_DIR / f"{media_id}{ext}"
            if p.exists():
                return p
    default = IMAGE_DIR / "img2.png"
    return default if default.exists() else None


def _make_image_clip(img: Path, out_path: Path, sec: float) -> bool:
    cmd = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        str(img),
        "-t",
        str(max(0.5, sec)),
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


def _make_segment(
    clip_in: Path,
    audio_in: Path,
    out_path: Path,
    target_sec: float,
) -> bool:
    # 视频循环到音频时长，统一参数，便于 concat demuxer copy
    cmd = [
        "ffmpeg",
        "-y",
        "-stream_loop",
        "-1",
        "-i",
        str(clip_in),
        "-i",
        str(audio_in),
        "-t",
        str(max(0.5, target_sec)),
        "-vf",
        "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=24",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-shortest",
        str(out_path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0 and out_path.exists() and out_path.stat().st_size > 0


def _concat_segments(seg_paths: list[Path], out_path: Path) -> bool:
    list_file = out_path.parent / "concat_segments.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for p in seg_paths:
            f.write(f"file '{p.absolute()}'\n")
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(out_path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    list_file.unlink(missing_ok=True)
    return r.returncode == 0 and out_path.exists() and out_path.stat().st_size > 0


async def main_async(args: argparse.Namespace) -> int:
    work_dir = WORK_ROOT / args.date
    clips_dir = work_dir / "clips"
    audio_dir = work_dir / "shot_audio"
    seg_dir = work_dir / "segments"
    EPISODE_DIR.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)
    seg_dir.mkdir(parents=True, exist_ok=True)

    plan_path = work_dir / "shot_plan.json"
    if not plan_path.exists():
        print(f"shot plan missing: {plan_path}", file=sys.stderr)
        return 1
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    shots: list[dict[str, Any]] = plan.get("shots") or []
    if not shots:
        print("shot plan has no shots", file=sys.stderr)
        return 1

    target = int(args.target_seconds)
    acc = 0.0
    srt_lines: list[str] = []
    seg_paths: list[Path] = []
    srt_index = 1

    for shot in shots:
        shot_id = int(shot["shot_id"])
        text = str(shot.get("text") or "").strip()
        role_id = str(shot.get("role_id") or "alice")
        media_id = shot.get("media_id")
        if not text:
            continue
        if acc >= target:
            break

        audio_path = audio_dir / f"shot_{shot_id:04d}.mp3"
        if not audio_path.exists() or audio_path.stat().st_size == 0 or args.force:
            ok = await _tts_one(text, role_id, audio_path)
            if not ok:
                print(f"tts failed for shot {shot_id}", file=sys.stderr)
                continue
        audio_sec = _probe_duration_sec(audio_path, fallback=float(shot.get("duration_sec") or 10))
        remain = target - acc
        seg_sec = min(audio_sec, remain)
        if seg_sec <= 0.2:
            break

        clip_path = clips_dir / f"shot_{shot_id:04d}.mp4"
        if (not clip_path.exists() or clip_path.stat().st_size == 0) and args.allow_image_fallback:
            img = _pick_fallback_image(media_id if isinstance(media_id, str) else None)
            if img:
                clip_path = seg_dir / f"fallback_shot_{shot_id:04d}.mp4"
                _make_image_clip(img, clip_path, seg_sec)
        if not clip_path.exists() or clip_path.stat().st_size == 0:
            print(f"missing clip for shot {shot_id}, skipped", file=sys.stderr)
            continue

        seg_out = seg_dir / f"seg_{len(seg_paths):04d}.mp4"
        ok = _make_segment(clip_path, audio_path, seg_out, seg_sec)
        if not ok:
            print(f"segment build failed for shot {shot_id}", file=sys.stderr)
            continue
        seg_paths.append(seg_out)

        start = acc
        end = acc + seg_sec
        srt_lines.append(str(srt_index))
        srt_lines.append(f"{_format_srt_time(start)} --> {_format_srt_time(end)}")
        srt_lines.append(f"{role_id}: {text}")
        srt_lines.append("")
        srt_index += 1
        acc = end

    if not seg_paths:
        print("no valid segments to assemble", file=sys.stderr)
        return 2

    out_mp4 = EPISODE_DIR / f"{args.date}_30min.mp4"
    ok = _concat_segments(seg_paths, out_mp4)
    if not ok:
        print("concat failed", file=sys.stderr)
        return 3

    # 时长兜底：若 concat 结果略小于 target，补一个冻结尾帧片段
    final_sec = _probe_duration_sec(out_mp4, fallback=acc)
    if final_sec + 0.2 < target:
        tail_gap = target - final_sec
        tail_src = seg_paths[-1]
        tail_clip = seg_dir / "tail_pad.mp4"
        cmd = [
            "ffmpeg",
            "-y",
            "-stream_loop",
            "-1",
            "-i",
            str(tail_src),
            "-t",
            str(tail_gap),
            "-an",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(tail_clip),
        ]
        subprocess.run(cmd, capture_output=True, text=True)
        if tail_clip.exists():
            all_paths = seg_paths + [tail_clip]
            _concat_segments(all_paths, out_mp4)
            final_sec = _probe_duration_sec(out_mp4, fallback=target)

    # 写字幕
    srt_path = work_dir / "episode.srt"
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")

    print(f"output: {out_mp4}")
    print(f"duration: {final_sec:.2f}s")
    print(f"subtitle: {srt_path}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Assemble 30min episode video from generated clips.")
    ap.add_argument("date", help="Episode date, e.g. 2026-03-05")
    ap.add_argument("--target-seconds", type=int, default=1800, help="Target duration seconds")
    ap.add_argument("--allow-image-fallback", action="store_true", help="Use image clips for missing shots")
    ap.add_argument("--force", action="store_true", help="Regenerate shot audios")
    args = ap.parse_args()

    try:
        import edge_tts  # noqa: F401
    except Exception:
        print("edge-tts not installed. Run: python3 -m pip install edge-tts", file=sys.stderr)
        return 1
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    sys.exit(main())
