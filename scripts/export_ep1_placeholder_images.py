#!/usr/bin/env python3
"""
从第一集对话 2026-03-05.json 中读取所有图片块，为每个 media_id 生成占位图 SVG，
写入 backend/media/images/，供 GET /api/media/image/{media_id} 直接返回。
这样第一集对话中每处图片位都有对应文件，无需实时生成。
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BACKEND = REPO / "backend"
DATA_DIR = BACKEND / "data" / "conversations"
IMAGE_DIR = BACKEND / "media" / "images"

# 使用 backend 的占位图逻辑
sys.path.insert(0, str(BACKEND))
from routes.media import svg_image_placeholder

EP1 = "2026-03-05.json"


def main():
    path = DATA_DIR / EP1
    if not path.is_file():
        print(f"Not found: {path}")
        return 1
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for msg in data.get("messages") or []:
        for block in msg.get("content_blocks") or []:
            if block.get("type") != "image" or not block.get("media_id"):
                continue
            media_id = block["media_id"]
            description = (block.get("description") or media_id).strip()
            svg = svg_image_placeholder(description, title="零号营地")
            out = IMAGE_DIR / f"{media_id}.svg"
            out.write_text(svg, encoding="utf-8")
            print(f"  {media_id}.svg  <- {description[:40]}...")
            count += 1
    print(f"Done: {count} placeholder image(s) in {IMAGE_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
