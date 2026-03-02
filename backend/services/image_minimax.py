"""
MiniMax 文生图（Text-to-Image）：根据文字描述生成图片。
需配置 MINIMAX_API_KEY。可选 MINIMAX_IMAGE_BASE（默认 https://api.minimax.io）。
文档：https://platform.minimax.io/docs/guides/image-generation
"""
import base64
import os
import requests
from typing import Optional

# 默认使用国际站；国内若需可设 MINIMAX_IMAGE_BASE=https://api.minimaxi.com
DEFAULT_BASE = "https://api.minimax.io"


def generate_image(
    prompt: str,
    aspect_ratio: str = "16:9",
    model: str = "image-01",
) -> Optional[bytes]:
    """
    调用 MiniMax 文生图，返回图片字节（PNG/JPEG）；失败返回 None。
    prompt: 图片描述，建议简洁英文或中文，最多约 1500 字。
    """
    api_key = os.environ.get("MINIMAX_API_KEY")
    if not api_key:
        return None
    prompt = (prompt or "").strip()[:1500]
    if not prompt:
        return None

    base_url = (os.environ.get("MINIMAX_IMAGE_BASE") or DEFAULT_BASE).rstrip("/")
    url = f"{base_url}/v1/image_generation"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "response_format": "base64",
        "n": 1,
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        if r.status_code != 200:
            if os.environ.get("MINIMAX_IMAGE_DEBUG"):
                import sys
                print(f"[Image] HTTP {r.status_code} {r.text[:500]}", file=sys.stderr)
            return None
        body = r.json()
        data = body.get("data") or {}
        images_b64 = data.get("image_base64") or data.get("images")
        if not images_b64 or not isinstance(images_b64, list):
            if os.environ.get("MINIMAX_IMAGE_DEBUG"):
                import sys
                print(f"[Image] No image_base64 in response: {list(body.keys())}", file=sys.stderr)
            return None
        raw = base64.b64decode(images_b64[0])
        return raw if raw else None
    except Exception as e:
        if os.environ.get("MINIMAX_IMAGE_DEBUG"):
            import sys
            print(f"[Image] Exception: {e}", file=sys.stderr)
        return None
