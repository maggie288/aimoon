# 零号营地提示词目录

本目录用于存放预生成对话与日报时使用的提示词，便于统一管理与迭代。

建议文件：

- `global_system.txt` — 全局系统提示词（场景、物理约束、输出格式、交互风格）
- `role_elena.txt` — 科幻作家 Elena Cosmos 专属提示词
- `role_chenwei.txt` — 物理科学家 Dr. Chen Wei 专属提示词
- `role_alice.txt` — 计算机科学家 Alice Nexus 专属提示词
- `role_oldtom.txt` — 机械师 Old Tom 专属提示词
- `flow_control.txt` — 对话流程控制（开场 / 主题讨论 / 方案综合 / 风险评估 / 总结）
- `daily_report.txt` — 日报生成提示词（论文结构）

接入 LLM 时，由 `scripts/generate_next_day.py` 或后端服务读取上述文件组装 prompt。
