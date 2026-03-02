"""
MiniMax T2A V2 语音合成：对齐官方 /v1/t2a_v2 接口。
需配置环境变量 MINIMAX_API_KEY、MINIMAX_GROUP_ID。
可选：MINIMAX_API_BASE（默认 https://api.minimaxi.com）、MINIMAX_TTS_MODEL。
音色 ID 见官方系统音色列表：https://platform.minimax.io/faq/system-voice-id
"""
import base64
import os
import requests
from typing import Optional

# 四角色音色：使用 MiniMax 开放平台「系统音色列表」中的 Voice ID（中文普通话）
# 列表见 https://platform.minimaxi.com/docs/faq/system-voice-id
VOICE_IDS = {
    "elena": "Chinese (Mandarin)_Wise_Women",     # 科幻作家：阅历姐姐/叙事感
    "chenwei": "Chinese (Mandarin)_Reliable_Executive",  # 物理科学家：沉稳高管
    "alice": "Chinese (Mandarin)_Sweet_Lady",       # 计算机科学家：甜美女声/清晰
    "oldtom": "Chinese (Mandarin)_Male_Announcer", # 机械师：播报男声/偏粗犷
}

DEFAULT_VOICE = "Chinese (Mandarin)_Male_Announcer"


def _decode_audio(audio_str: str) -> Optional[bytes]:
    """Decode audio string: try hex first (t2a_v2 default), then base64."""
    if not audio_str or not isinstance(audio_str, str):
        return None
    s = audio_str.strip()
    # Try hex: even length and all hex chars
    if len(s) % 2 == 0 and all(c in "0123456789abcdefABCDEF" for c in s):
        try:
            return bytes.fromhex(s)
        except (ValueError, TypeError):
            pass
    try:
        return base64.b64decode(s)
    except Exception:
        return None


def synthesize(text: str, voice_id: str) -> Optional[bytes]:
    """调用 MiniMax T2A V2，返回 MP3 音频字节；失败返回 None。"""
    api_key = os.environ.get("MINIMAX_API_KEY")
    group_id = os.environ.get("MINIMAX_GROUP_ID")
    if not api_key or not group_id:
        return None
    text = (text or "").strip()
    if not text:
        return None

    base_url = (os.environ.get("MINIMAX_API_BASE") or "https://api.minimaxi.com").rstrip("/")
    path = "/v1/t2a_v2"
    query = f"?GroupId={group_id}" if group_id else ""
    url = f"{base_url}{path}{query}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    model = os.environ.get("MINIMAX_TTS_MODEL") or "speech-2.6-hd"
    payload = {
        "model": model,
        "text": text[:10000],
        "stream": False,
        "output_format": "hex",
        "language_boost": "Chinese",
        "voice_setting": {
            "voice_id": VOICE_IDS.get(voice_id, DEFAULT_VOICE),
            "speed": 1.0,
            "vol": 1.0,
            "pitch": 0,
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 1,
        },
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        if r.status_code != 200:
            if os.environ.get("MINIMAX_TTS_DEBUG"):
                import sys
                print(f"[TTS] HTTP {r.status_code} {r.text[:500]}", file=sys.stderr)
            return None
        body = r.json()
        base_resp = body.get("base_resp") or {}
        if base_resp.get("status_code") != 0:
            if os.environ.get("MINIMAX_TTS_DEBUG"):
                import sys
                print(f"[TTS] API status_code={base_resp.get('status_code')} status_msg={base_resp.get('status_msg')}", file=sys.stderr)
            return None
        data = body.get("data")
        if data is None:
            return None
        audio_str = data.get("audio")
        if not isinstance(audio_str, str):
            return None
        return _decode_audio(audio_str)
    except Exception as e:
        if os.environ.get("MINIMAX_TTS_DEBUG"):
            import sys
            print(f"[TTS] Exception: {e}", file=sys.stderr)
        return None
