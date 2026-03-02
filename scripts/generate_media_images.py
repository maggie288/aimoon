#!/usr/bin/env python3
"""
根据对话 JSON 中的图片块描述，调用 MiniMax 文生图生成图片并保存到 backend/media/images/。
后端 GET /api/media/image/{media_id} 会优先返回这些文件，否则返回占位 SVG。

使用前：
  - 配置 backend/.env 中的 MINIMAX_API_KEY（文生图可用国际 api.minimax.io 或国内 api.minimaxi.com）
  - 可选：MINIMAX_IMAGE_BASE、MINIMAX_IMAGE_DEBUG=1
  - cd backend && pip install requests python-dotenv

运行：
  python scripts/generate_media_images.py [--dry-run] [--lang en]
  --dry-run  只列出将要生成的 media_id，不调用 API
  --lang en 只处理 *-en.json 中的图片（用于生成英文版插图）
"""
import argparse
import json
import os
import sys
from pathlib import Path

# 加载 backend 环境与模块
REPO = Path(__file__).resolve().parent.parent
BACKEND = REPO / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

from dotenv import load_dotenv
load_dotenv(BACKEND / ".env")

from services.image_minimax import generate_image

DATA_DIR = BACKEND / "data" / "conversations"
IMAGE_DIR = BACKEND / "media" / "images"


def collect_image_blocks(lang: str = ""):
    """从 data/conversations/*.json 收集 (media_id, description)。"""
    suffix = "-en.json" if lang == "en" else ".json"
    if lang == "en":
        files = list(DATA_DIR.glob("*-en.json"))
    else:
        files = [f for f in DATA_DIR.glob("*.json") if not f.name.endswith("-en.json")]
    seen = {}
    for path in sorted(files):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Skip {path.name}: {e}", file=sys.stderr)
            continue
        for msg in data.get("messages") or []:
            for block in msg.get("content_blocks") or []:
                if block.get("type") == "image" and block.get("media_id"):
                    mid = block["media_id"]
                    desc = (block.get("description") or mid).strip()
                    if mid and mid not in seen:
                        seen[mid] = desc
    return seen


def main():
    ap = argparse.ArgumentParser(description="Generate images from conversation image blocks via MiniMax.")
    ap.add_argument("--dry-run", action="store_true", help="Only list media_id, do not call API")
    ap.add_argument("--lang", default="", help="Process only *-en.json when set to 'en'")
    args = ap.parse_args()

    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    items = collect_image_blocks(args.lang)
    if not items:
        print("No image blocks found in conversations.")
        return

    print(f"Found {len(items)} image block(s).")
    for media_id, description in items.items():
        if any((IMAGE_DIR / f"{media_id}{e}").is_file() for e in (".png", ".jpg", ".jpeg", ".webp")):
            print(f"  [skip] {media_id} (already exists)")
            continue
        if args.dry_run:
            print(f"  [would generate] {media_id}: {description[:50]}...")
            continue
        # 描述作为 prompt；文生图对长描述会截断，保留前 500 字
        prompt = description[:500] if len(description) > 500 else description
        print(f"  [gen] {media_id} ...")
        raw = generate_image(prompt, aspect_ratio="16:9")
        if raw:
            # MiniMax 可能返回 JPEG；按魔数选择扩展名
            ext = ".jpg" if raw[:2] == b"\xff\xd8" else ".png"
            out = IMAGE_DIR / f"{media_id}{ext}"
            out.write_bytes(raw)
            print(f"    -> {out}")
        else:
            print(f"    -> failed (check MINIMAX_API_KEY / balance / MINIMAX_IMAGE_DEBUG=1)")


if __name__ == "__main__":
    main()
