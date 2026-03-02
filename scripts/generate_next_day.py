#!/usr/bin/env python3
"""
预生成「下一天」的对话脚本。
用法: python scripts/generate_next_day.py [date]
例如: python scripts/generate_next_day.py 2026-03-06
依赖: 需配置 LLM API（如 OPENAI_API_KEY）及 backend/data/prompts/ 下的提示词。
当前为占位：仅复制模板并写入空对话骨架，实际内容需接 LLM 生成。
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "backend" / "data"
CONV_DIR = DATA / "conversations"
TOPICS_PATH = DATA / "topics.json"


def load_topics():
    with open(TOPICS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_topic_for_date(date: str):
    topics = load_topics()
    for t in topics:
        if t.get("date") == date:
            return t
    return None


def main():
    date = sys.argv[1] if len(sys.argv) > 1 else None
    if not date:
        print("用法: python scripts/generate_next_day.py YYYY-MM-DD")
        sys.exit(1)

    topic = get_topic_for_date(date)
    if not topic:
        print(f"未找到日期 {date} 的话题，请检查 backend/data/topics.json")
        sys.exit(1)

    out_path = CONV_DIR / f"{date}.json"
    if out_path.exists():
        print(f"已存在 {out_path}，跳过。若要重新生成请先删除。")
        sys.exit(0)

    # 占位：仅写骨架。后续可在此调用 LLM + prompts 生成完整 messages。
    skeleton = {
        "date": date,
        "day": topic["day"],
        "topic_title": topic["topic_title"],
        "topic_description": topic.get("topic_description", ""),
        "phase": topic.get("phase", ""),
        "messages": [
            {
                "role_id": "alice",
                "timestamp": "08:00",
                "content_blocks": [
                    {
                        "type": "paragraph",
                        "content": f"【今日话题】{topic['topic_title']}\n【核心问题】{topic.get('topic_description', '')}\n（本日对话由 generate_next_day + LLM 生成，当前为占位。）"
                    }
                ]
            }
        ]
    }

    CONV_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(skeleton, f, ensure_ascii=False, indent=2)

    print(f"已写入 {out_path}（占位）。接 LLM 后可在本脚本中生成完整对话。")


if __name__ == "__main__":
    main()
