"""
零号营地 - 四角色 Agent 对话 API
"""
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, Response
import json

from services.doc_generator import build_daily_report_md
from services.tts_minimax import synthesize as tts_synthesize

from routes.media import router as media_router

app = FastAPI(title="零号营地 API", version="0.1.0")
app.include_router(media_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent / "data"


def load_json(name: str):
    p = DATA_DIR / name
    if not p.exists():
        return None
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/topics")
def get_topics(lang: str = None):
    """30 天话题列表；lang=en 时返回英文版 topics-en.json"""
    filename = "topics-en.json" if lang == "en" else "topics.json"
    data = load_json(filename)
    if data is None:
        raise HTTPException(status_code=500, detail=f"{filename} not found")
    return data


@app.get("/api/topics/{date}")
def get_topic_by_date(date: str):
    """按日期取单日话题 (YYYY-MM-DD)"""
    topics = load_json("topics.json")
    if not topics:
        raise HTTPException(status_code=500, detail="topics not found")
    for t in topics:
        if t.get("date") == date:
            return t
    raise HTTPException(status_code=404, detail=f"topic not found for {date}")


@app.get("/api/agents")
def get_agents(lang: str = Query(None, description="en=英文角色名与职称")):
    """四角色信息；lang=en 时返回英文版 agents-en.json（英文名/职称/代号），否则中文。"""
    filename = "agents-en.json" if (lang or "").strip().lower() == "en" else "agents.json"
    data = load_json(filename)
    if data is None:
        raise HTTPException(status_code=500, detail=f"{filename} not found")
    return data


@app.get("/api/conversations/{date}")
def get_conversation(date: str, lang: str = None):
    """按日期取当日对话 (YYYY-MM-DD)。lang=en 时加载 {date}-en.json。"""
    name = f"{date}-en.json" if (lang or "").strip().lower() == "en" else f"{date}.json"
    path = DATA_DIR / "conversations" / name
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"conversation not found for {date}" + (f" (lang={lang})" if lang else ""))
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "zerocamp-api"}


@app.get("/api/daily-report/{date}", response_class=PlainTextResponse)
def get_daily_report(date: str):
    """当日日报（论文格式 Markdown），可下载。"""
    path = DATA_DIR / "conversations" / f"{date}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"conversation not found for {date}")
    with open(path, "r", encoding="utf-8") as f:
        conv = json.load(f)

    topics = load_json("topics.json")
    topic = next((t for t in (topics or []) if t.get("date") == date), {})
    md = build_daily_report_md(conv, topic)

    filename = f"zerocamp-day{conv.get('day', 0)}-{date}.md"
    return PlainTextResponse(
        md,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


from pydantic import BaseModel


class TTSRequest(BaseModel):
    text: str = ""
    voice_id: str = "alice"


@app.post("/api/tts/synthesize")
def api_tts_synthesize(req: TTSRequest):
    """MiniMax 2.x TTS：传入 JSON { text, voice_id }，返回 MP3。未配置时 404，前端可回退浏览器朗读。"""
    text = req.text or ""
    voice_id = req.voice_id or "alice"
    audio = tts_synthesize(text, voice_id)
    if not audio:
        raise HTTPException(status_code=404, detail="TTS not configured or synthesis failed")
    return Response(content=audio, media_type="audio/mpeg")
