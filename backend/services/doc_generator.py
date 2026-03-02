"""
当日对话 → 论文格式日报（Markdown）
"""
import json
from pathlib import Path


def _collect_text(blocks: list) -> str:
    parts = []
    for b in blocks:
        if b.get("type") == "paragraph" and b.get("content"):
            parts.append(b["content"].strip())
        if b.get("type") == "math" and b.get("content"):
            parts.append(f"$${b['content']}$$")
    return "\n\n".join(parts) if parts else ""


def _role_section_name(role_id: str) -> str:
    names = {
        "alice": "计算机科学家",
        "chenwei": "物理科学家",
        "oldtom": "机械师",
        "elena": "科幻作家",
    }
    return names.get(role_id, role_id)


def build_daily_report_md(conv: dict, topic: dict) -> str:
    """从当日对话与话题生成论文格式 Markdown。"""
    day = conv.get("day", 0)
    date = conv.get("date", "")
    title_zh = conv.get("topic_title", "")
    phase = conv.get("phase", "")
    messages = conv.get("messages", [])

    # 按角色聚合段落
    by_role: dict[str, list[str]] = {}
    for msg in messages:
        rid = msg.get("role_id", "")
        text = _collect_text(msg.get("content_blocks", []))
        if not text:
            continue
        if rid not in by_role:
            by_role[rid] = []
        by_role[rid].append(text)

    # 摘要：话题描述 + 首条
    first_text = ""
    for msg in messages:
        for b in msg.get("content_blocks", []):
            if b.get("type") == "paragraph" and b.get("content"):
                first_text = b["content"][:200] + "…" if len(b["content"]) > 200 else b["content"]
                break
        if first_text:
            break
    abstract = f"本文记录零号营地第{day}天技术讨论，主题为「{title_zh}」。{conv.get('topic_description', '')} 讨论要点：{first_text}"

    lines = [
        f"# 第{day}天 零号营地任务日志：{title_zh}",
        f"# Day {day} Mission Log: {title_zh}",
        "",
        f"**日期** {date} · **阶段** {phase}",
        "",
        "## 摘要",
        "",
        abstract,
        "",
        "---",
        "",
        "## 1. 问题背景",
        "",
        topic.get("topic_description", ""),
        "",
        "## 2. 物理约束分析",
        "",
    ]
    for t in by_role.get("chenwei", []):
        lines.append("- " + t.replace("\n\n", " "))
        lines.append("")
    lines.extend(["## 3. 系统架构设计", ""])
    for t in by_role.get("alice", []):
        lines.append("- " + t.replace("\n\n", " "))
        lines.append("")
    lines.extend(["## 4. 工程实现考量", ""])
    for t in by_role.get("oldtom", []):
        lines.append("- " + t.replace("\n\n", " "))
        lines.append("")
    lines.extend(["## 5. 人类因素分析", ""])
    for t in by_role.get("elena", []):
        lines.append("- " + t.replace("\n\n", " "))
        lines.append("")
    lines.extend([
        "## 6. 风险评估",
        "",
        "| 风险项 | 概率 | 影响 | 缓解措施 |",
        "|--------|------|------|----------|",
        "| 密封失效未及时发现 | 中 | 严重 | 双通道检漏、明确漏率上限 |",
        "| 电池/热控不足 6 小时 | 中 | 严重 | 最低负载清单、冗余与降级 |",
        "| 通信长时间中断 | 低 | 一般 | 心跳与超时约定、本地缓存与过顶补传 |",
        "",
        "## 7. 结论与下一步",
        "",
        "当日讨论形成 6 小时执行框架：密封检漏 → 电与热 → 通信心跳 → 轮值监控；全程复诵与超时升级。",
        "",
        "明日话题见 topics 表。",
        "",
    ])
    return "\n".join(lines)
