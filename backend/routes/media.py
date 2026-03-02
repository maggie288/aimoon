"""媒体占位：图片 SVG 或 MiniMax 文生图缓存；视频为 Manim 生成的 MP4（若有）"""
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, Response

router = APIRouter(prefix="/api/media", tags=["media"])

# 项目 media 目录
_MEDIA_ROOT = Path(__file__).resolve().parent.parent / "media"
# Manim 渲染的 MP4 存放目录；运行 scripts/render_manim_videos.py 生成
VIDEO_DIR = _MEDIA_ROOT / "videos"
# MiniMax 文生图缓存；运行 scripts/generate_media_images.py 生成
IMAGE_DIR = _MEDIA_ROOT / "images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)
# 预生成语音；运行 scripts/generate_ep1_audio.py 生成
AUDIO_DIR = _MEDIA_ROOT / "audio"


def _escape_svg(s: str) -> str:
    """SVG/XML 内文本转义。"""
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;")


def _wrap_text(text: str, chars_per_line: int = 28) -> list[str]:
    """将长文本按字符数拆成多行，尽量在标点后断行。"""
    text = (text or "").strip().replace('"', "'")
    if not text:
        return ["示意图"]
    if len(text) <= chars_per_line:
        return [text[:80]]
    lines: list[str] = []
    rest = text[:120]  # 最多显示约 120 字
    while rest:
        if len(rest) <= chars_per_line:
            lines.append(rest)
            break
        # 在 chars_per_line 内找最后一个标点或直接截断
        chunk = rest[:chars_per_line]
        for sep in "。，、；：":
            i = chunk.rfind(sep)
            if i > 0:
                lines.append(chunk[: i + 1])
                rest = rest[i + 1 :].lstrip()
                break
        else:
            lines.append(chunk)
            rest = rest[chars_per_line:].lstrip()
    return lines[:6]  # 最多 6 行


def svg_image_placeholder(label: str, title: str = "零号营地") -> str:
    """生成深色主题的占位图 SVG，长说明自动换行多行显示。"""
    safe_title = (title or "零号营地").replace('"', "'")
    lines = _wrap_text(label)
    # 每行一个 <tspan>，从 y≈160 起，行高约 22
    y_start = 150
    line_height = 22
    tspans = "\n".join(
        f'    <tspan x="320" dy="{line_height if i else 0}" text-anchor="middle">{_escape_svg(ln)}</tspan>'
        for i, ln in enumerate(lines)
    )
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">
  <rect width="640" height="360" fill="#0f0f11"/>
  <rect x="1" y="1" width="638" height="358" fill="none" stroke="#2d2d32" stroke-width="1" rx="8"/>
  <text x="320" y="{y_start}" fill="#71717a" font-size="14" font-family="system-ui,sans-serif">{_escape_svg(safe_title)}</text>
  <text x="320" y="{y_start + 28}" fill="#52525b" font-size="12" font-family="system-ui,sans-serif">
{tspans}
  </text>
</svg>'''


@router.get("/image/{media_id}")
def get_image(
    media_id: str,
    label: str = Query(None, description="图片说明，用于占位图显示"),
):
    """优先返回已生成的图片（IMAGE_DIR 下）；若无则返回占位 SVG。"""
    if media_id and ".." not in media_id and "/" not in media_id:
        for ext in (".png", ".jpg", ".jpeg", ".webp", ".svg"):
            path = IMAGE_DIR / f"{media_id}{ext}"
            if path.is_file():
                mt = "image/svg+xml" if ext == ".svg" else f"image/{ext.lstrip('.')}"
                return FileResponse(path, media_type=mt)
    svg = svg_image_placeholder(label or media_id)
    return Response(content=svg, media_type="image/svg+xml")


@router.get("/video/{media_id}")
def get_video(media_id: str):
    """返回 Manim 生成的 MP4；若不存在则 404，前端显示占位卡片。"""
    if not media_id or ".." in media_id or "/" in media_id:
        raise HTTPException(status_code=400, detail="invalid media_id")
    mp4_path = VIDEO_DIR / f"{media_id}.mp4"
    if mp4_path.is_file():
        return FileResponse(mp4_path, media_type="video/mp4")
    raise HTTPException(status_code=404, detail="video not found; run scripts/render_manim_videos.py to generate")


@router.get("/audio/{date}/{index}")
def get_audio(date: str, index: int, lang: str = None):
    """返回预生成的单条语音 MP3；lang=en 时从 {date}-en 目录取英文语音。"""
    if not date or ".." in date or "/" in date or index < 0 or index > 9999:
        raise HTTPException(status_code=400, detail="invalid date or index")
    subdir = f"{date}-en" if lang == "en" else date
    mp3_path = AUDIO_DIR / subdir / f"{index:03d}.mp3"
    if mp3_path.is_file():
        return FileResponse(mp3_path, media_type="audio/mpeg")
    raise HTTPException(status_code=404, detail="audio not found")