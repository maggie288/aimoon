#!/usr/bin/env python3
"""
用 edge-tts（本机，免费）为指定集数中文对话（{date}.json）预生成 4 角色语音。
生成到 backend/media/audio/{date}/{index:03d}.mp3，播放时优先使用。

依赖：pip install edge-tts
运行：python scripts/generate_ep_audio.py [date]
      python scripts/generate_ep_audio.py 2026-03-05   # 第1集
      python scripts/generate_ep_audio.py 2026-03-06   # 第2集
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import List, Optional

REPO = Path(__file__).resolve().parent.parent
BACKEND = REPO / "backend"
DATA_DIR = BACKEND / "data" / "conversations"
AUDIO_DIR = BACKEND / "media" / "audio"

# 四角色 → edge-tts 中文音色 + 语速/音调（拟人化）
VOICE_CONFIG = {
    "chenwei": {"voice": "zh-CN-YunyangNeural", "rate": "-2%", "pitch": "+0Hz"},
    "alice":   {"voice": "zh-CN-XiaoxiaoNeural", "rate": "+3%", "pitch": "+1Hz"},
    "oldtom":  {"voice": "zh-CN-YunxiNeural",    "rate": "-4%", "pitch": "-2Hz"},
    "elena":   {"voice": "zh-CN-XiaoyiNeural",  "rate": "+0%", "pitch": "+0Hz"},
}


def get_message_text(msg: dict) -> str:
    parts = []
    for b in msg.get("content_blocks") or []:
        if b.get("type") == "paragraph" and b.get("content"):
            parts.append(b["content"].strip())
    return " ".join(parts)


def normalize_tts_text(text: str) -> str:
    """替换可能导致 edge-tts 无响应的字符（如 Unicode 下标）。"""
    if not text:
        return text
    # Unicode 下标 → 普通数字，避免 "No audio was received"
    t = text.replace("\u2082", "2").replace("\u2081", "1")  # ₂ ₁
    t = t.replace("\u2090", "0")  # ₀
    return t


async def generate_one(voice: str, rate: str, pitch: str, text: str, out_path: Path) -> bool:
    import asyncio
    text = normalize_tts_text(text)
    for attempt in range(3):
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
            await communicate.save(str(out_path))
            if out_path.stat().st_size == 0:
                raise RuntimeError("Saved file is 0 bytes")
            return True
        except Exception as e:
            print(f"    error (attempt {attempt + 1}/3): {e}", file=sys.stderr)
            if attempt < 2:
                await asyncio.sleep(2)
    return False


async def main_async(date: str, dry_run: bool, only_indices: Optional[List[int]]):
    path = DATA_DIR / f"{date}.json"
    if not path.is_file():
        print(f"Not found: {path}")
        return 1
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    out_dir = AUDIO_DIR / date
    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    messages = data.get("messages") or []
    total = 0
    for i, msg in enumerate(messages):
        if only_indices is not None and i not in only_indices:
            continue
        text = get_message_text(msg)
        if not text.strip():
            continue
        role_id = msg.get("role_id") or "alice"
        cfg = VOICE_CONFIG.get(role_id, VOICE_CONFIG["alice"])
        out_path = out_dir / f"{i:03d}.mp3"
        if dry_run:
            print(f"  [would] {i:03d}.mp3 {role_id} ({len(text)} chars)")
            total += 1
            continue
        print(f"  [gen] {i:03d}.mp3 {role_id} ...")
        ok = await generate_one(
            cfg["voice"], cfg["rate"], cfg["pitch"],
            text[:5000],
            out_path,
        )
        if ok:
            total += 1
            print(f"    -> {out_path}")
    print(f"Done: {total} audio file(s) in {out_dir}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Pre-generate Chinese TTS for an episode (date.json) with edge-tts.")
    ap.add_argument("date", nargs="?", default="2026-03-05", help="Episode date, e.g. 2026-03-06")
    ap.add_argument("--dry-run", action="store_true", help="Only list messages, do not generate")
    ap.add_argument("--only-indices", type=str, default=None, help="Comma-separated indices to generate, e.g. 79,81,85")
    args = ap.parse_args()
    only_indices = None
    if args.only_indices:
        only_indices = [int(x.strip()) for x in args.only_indices.split(",")]
    try:
        import edge_tts  # noqa: F401
    except ImportError:
        print("Install: pip install edge-tts", file=sys.stderr)
        return 1
    return asyncio.run(main_async(args.date, args.dry_run, only_indices))


if __name__ == "__main__":
    sys.exit(main())
