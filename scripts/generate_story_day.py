#!/usr/bin/env python3
"""
按 docs/storyline-design.md 与 backend/data/topics.json 生成单集对话。
用法: python scripts/generate_story_day.py <date>
例如: python scripts/generate_story_day.py 2026-03-06

支持本地/远程 OpenAI 兼容 API：
- 本地 Ollama: 设置 OPENAI_API_BASE=http://localhost:11434/v1, OPENAI_API_KEY=ollama
- 或设置 OPENAI_API_KEY 使用 OpenAI/其他兼容服务

输出: backend/data/conversations/<date>.json（若已存在则跳过，加 --overwrite 可覆盖）
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "backend" / "data"
CONV_DIR = DATA / "conversations"
PROMPTS_DIR = DATA / "prompts"


def load_json(name: str):
    path = DATA / name
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_topic(date: str):
    topics = load_json("topics.json")
    if not topics:
        return None
    for t in topics:
        if t.get("date") == date:
            return t
    return None


def build_user_prompt(topic: dict) -> str:
    return f"""请生成「第 {topic['day']} 天」的完整圆桌对话。

【故事标题】{topic['topic_title']}
【核心事件】{topic['topic_description']}
【情感主题】{topic.get('emotional_theme', '')}
【技术要点】{', '.join(topic.get('core_points', []))}

严格按 system 中的 JSON 数组格式输出，不要 markdown 代码块包裹，不要其他说明。"""


def call_llm(system: str, user: str) -> str:
    try:
        import openai
    except ImportError:
        print("请安装 openai: pip install openai")
        sys.exit(1)

    api_key = os.environ.get("OPENAI_API_KEY")
    base = os.environ.get("OPENAI_API_BASE")
    if not api_key and not base:
        print("未设置 OPENAI_API_KEY 或 OPENAI_API_BASE。可用 Ollama: OPENAI_API_BASE=http://localhost:11434/v1 OPENAI_API_KEY=ollama")
        sys.exit(1)

    client = openai.OpenAI(api_key=api_key or "ollama", base_url=base)
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    if base and "ollama" in (base or ""):
        model = os.environ.get("OPENAI_MODEL", "llama3.2")

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.75,
    )
    return (resp.choices[0].message.content or "").strip()


def parse_messages(raw: str) -> list:
    """从 LLM 输出中解析出 messages 数组。"""
    raw = raw.strip()
    # 去掉 markdown 代码块 ```json ... ``` 或 ``` ... ```
    if "```" in raw:
        parts = re.split(r"```(?:\w*)\s*", raw, maxsplit=2)
        if len(parts) >= 2:
            raw = parts[1].rstrip().rstrip("`").strip()
    try:
        arr = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start >= 0 and end > start:
            arr = json.loads(raw[start:end])
        else:
            raise
    if not isinstance(arr, list):
        raise ValueError("输出不是 JSON 数组")
    out = []
    for i, m in enumerate(arr):
        if not isinstance(m, dict):
            continue
        role_id = m.get("role_id")
        if role_id not in ("alice", "chenwei", "elena", "oldtom"):
            continue
        ts = m.get("timestamp", "08:00")
        blocks = m.get("content_blocks") or []
        if not blocks:
            blocks = [{"type": "paragraph", "content": str(m.get("content", ""))[:500]}]
        out.append({"role_id": role_id, "timestamp": ts, "content_blocks": blocks})
    return out


def main():
    date = (sys.argv[1] if len(sys.argv) > 1 else "").strip()
    overwrite = "--overwrite" in sys.argv
    if not date or len(date) != 10:
        print("用法: python scripts/generate_story_day.py YYYY-MM-DD [--overwrite]")
        sys.exit(1)

    topic = get_topic(date)
    if not topic:
        print(f"未找到日期 {date} 的 topic，请检查 backend/data/topics.json")
        sys.exit(1)

    out_path = CONV_DIR / f"{date}.json"
    if out_path.exists() and not overwrite:
        print(f"已存在 {out_path}，跳过。使用 --overwrite 覆盖。")
        sys.exit(0)

    system_path = PROMPTS_DIR / "system_storyline.txt"
    system = system_path.read_text(encoding="utf-8") if system_path.exists() else ""
    user = build_user_prompt(topic)

    print(f"正在生成第 {topic['day']} 天：{topic['topic_title']} …")
    raw = call_llm(system, user)
    messages = parse_messages(raw)

    payload = {
        "date": date,
        "day": topic["day"],
        "topic_title": topic["topic_title"],
        "topic_description": topic.get("topic_description", ""),
        "phase": topic.get("phase", ""),
        "messages": messages,
    }
    CONV_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"已写入 {out_path}，共 {len(messages)} 条消息。")


if __name__ == "__main__":
    main()
