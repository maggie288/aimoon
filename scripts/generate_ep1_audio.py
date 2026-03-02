#!/usr/bin/env python3
"""
用 edge-tts（本机，免费）为第一集对话预生成 4 角色语音，拟人化语速与语调。
生成文件放到 backend/media/audio/2026-03-05/{index:03d}.mp3，播放时优先使用。

依赖：pip install edge-tts
运行：python scripts/generate_ep1_audio.py [--dry-run]
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
EP1_DATE = "2026-03-05"

# 四角色 → edge-tts 中文音色 + 语速/音调（拟人化）
# 语速 rate: 负值更慢、正值更快；音调 pitch: 单位 Hz
VOICE_CONFIG = {
    "chenwei": {"voice": "zh-CN-YunyangNeural", "rate": "-2%", "pitch": "+0Hz"},   # 沉稳
    "alice":   {"voice": "zh-CN-XiaoxiaoNeural", "rate": "+3%", "pitch": "+1Hz"},  # 清晰略活泼
    "oldtom":  {"voice": "zh-CN-YunxiNeural",    "rate": "-4%", "pitch": "-2Hz"},  # 偏慢、略沉
    "elena":   {"voice": "zh-CN-XiaoyiNeural",  "rate": "+0%", "pitch": "+0Hz"},   # 叙事感
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


async def main_async(dry_run: bool):
    path = DATA_DIR / f"{EP1_DATE}.json"
    if not path.is_file():
        print(f"Not found: {path}")
        return 1
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    out_dir = AUDIO_DIR / EP1_DATE
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
            text[:5000],  # edge-tts 单段不宜过长
            out_path,
        )
        if ok:
            total += 1
            print(f"    -> {out_path}")
    print(f"Done: {total} audio file(s) in {out_dir}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Pre-generate episode 1 TTS with edge-tts (4 voices).")
    ap.add_argument("--dry-run", action="store_true", help="Only list messages, do not generate")
    args = ap.parse_args()
    try:
        import edge_tts  # noqa: F401
    except ImportError:
        print("Install: pip install edge-tts", file=sys.stderr)
        return 1
    return asyncio.run(main_async(args.dry_run))


if __name__ == "__main__":
    sys.exit(main())
