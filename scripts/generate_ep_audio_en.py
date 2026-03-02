#!/usr/bin/env python3
"""
用 edge-tts 为指定集数英文对话（{date}-en.json）预生成英文语音。
生成到 backend/media/audio/{date}-en/{index:03d}.mp3，英文页播放时优先使用。

依赖：pip install edge-tts
运行：python scripts/generate_ep_audio_en.py [date]
      python scripts/generate_ep_audio_en.py 2026-03-06
      python scripts/generate_ep_audio_en.py 2026-03-05   # 第1集
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BACKEND = REPO / "backend"
DATA_DIR = BACKEND / "data" / "conversations"
AUDIO_DIR = BACKEND / "media" / "audio"

VOICE_CONFIG = {
    "chenwei": {"voice": "en-US-GuyNeural", "rate": "-2%", "pitch": "+0Hz"},
    "alice":   {"voice": "en-US-JennyNeural", "rate": "+2%", "pitch": "+0Hz"},
    "oldtom":  {"voice": "en-US-ChristopherNeural", "rate": "-2%", "pitch": "+0Hz"},
    "elena":   {"voice": "en-US-AriaNeural", "rate": "+0%", "pitch": "+0Hz"},
}


def get_message_text(msg: dict) -> str:
    parts = []
    for b in msg.get("content_blocks") or []:
        if b.get("type") == "paragraph" and b.get("content"):
            parts.append(b["content"].strip())
    return " ".join(parts)


async def generate_one(voice: str, rate: str, pitch: str, text: str, out_path: Path) -> bool:
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await communicate.save(str(out_path))
        return True
    except Exception as e:
        print(f"    error: {e}", file=sys.stderr)
        return False


async def main_async(date: str, dry_run: bool):
    path = DATA_DIR / f"{date}-en.json"
    if not path.is_file():
        print(f"Not found: {path}")
        return 1
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    out_subdir = f"{date}-en"
    out_dir = AUDIO_DIR / out_subdir
    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    messages = data.get("messages") or []
    total = 0
    for i, msg in enumerate(messages):
        text = get_message_text(msg)
        if not text.strip():
            continue
        role_id = msg.get("role_id") or "alice"
        cfg = VOICE_CONFIG.get(role_id, VOICE_CONFIG["alice"])
        out_path = out_dir / f"{i:03d}.mp3"
        if out_path.is_file() and not dry_run:
            print(f"  [skip] {i:03d}.mp3 ({role_id})")
            total += 1
            continue
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
    ap = argparse.ArgumentParser(description="Pre-generate English TTS for an episode (date-en.json).")
    ap.add_argument("date", nargs="?", default="2026-03-06", help="Episode date, e.g. 2026-03-06")
    ap.add_argument("--dry-run", action="store_true", help="Only list messages, do not generate")
    args = ap.parse_args()
    try:
        import edge_tts  # noqa: F401
    except ImportError:
        print("Install: pip install edge-tts", file=sys.stderr)
        return 1
    return asyncio.run(main_async(args.date, args.dry_run))


if __name__ == "__main__":
    sys.exit(main())
