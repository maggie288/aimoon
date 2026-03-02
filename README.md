# 零号营地 · 月球生存 30 天

四角色 AI Agent 圆桌对话网站：人类从 0 到 1 在月球生活。  
科幻作家、物理科学家、计算机科学家、机械师 —— 每日 30 分钟对话，生存 → 稳定 → 扩张 → 文明。

## 技术栈

- **前端**: Next.js 14 (App Router), Tailwind CSS, KaTeX, Mermaid
- **后端**: Python FastAPI，提供话题与对话 API
- **数据**: JSON（topics.json、agents.json、conversations/YYYY-MM-DD.json）

## 本地运行

### 1. 后端

```bash
cd backend
pip install -r requirements.txt   # 或 python3 -m pip install -r requirements.txt
uvicorn main:app --reload --port 8000   # 或 python3 -m uvicorn main:app --reload --port 8000
```

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 http://localhost:3000 。首页为 30 天话题列表，点击某日进入该日对话页（如 `/day/2026-03-05`）。

### 3. 预生成「下一天」对话脚本（占位）

```bash
python scripts/generate_next_day.py 2026-03-06
```

当前脚本仅写入占位骨架；接入 LLM 与 `backend/data/prompts/` 后可生成完整对话。

## 目录结构

- `frontend/` — Next.js 前端（黑色科技风）
- `backend/` — FastAPI + data（topics、agents、conversations）
- `scripts/` — 预生成脚本（如 generate_next_day.py）

## 第 1 天内容

第 1 天（2026-03-05）对话已按「画面增强版」脚本写入 `backend/data/conversations/2026-03-05.json`，含段落、公式、Mermaid、图片/视频块；剧集时长约 1 小时，已做部分扩充。

## 语音

播放时**优先使用预生成语音**（本机 edge-tts 生成，四角色不同音色与语速）：`GET /api/media/audio/{date}/{index}`。预生成：`pip install edge-tts` 后运行 `python scripts/generate_ep1_audio.py`。若无预生成则尝试 **MiniMax TTS**（需 `MINIMAX_API_KEY`、`MINIMAX_GROUP_ID`），最后回退浏览器朗读。

## 图片与视频

- **图片**：`GET /api/media/image/{media_id}?label=...` 返回占位 SVG；前端已用该接口加载对话中的图片。
- **视频**：`GET /api/media/video/{media_id}` 当前返回 404，前端显示占位卡片；后续可放入 Manim 渲染的 MP4 或占位视频文件。

## 部署到公网

**分步操作说明**见 **[docs/deploy.md](docs/deploy.md)**（Vercel + Railway / Render 从零到上线的完整步骤）。

### 后端（Railway / Render / Fly.io）

1. 将仓库推送到 GitHub，在平台新建项目并选择该仓库。
2. **根目录** 设为 `backend`（或仅部署 backend 目录）。
3. **启动命令**：`uvicorn main:app --host 0.0.0.0 --port $PORT`（平台会注入 `PORT`）；或 `sh run.sh`（需在 backend 目录下执行）。
4. **环境变量**（可选）：`MINIMAX_API_KEY`、`MINIMAX_GROUP_ID`（TTS）；无则回退浏览器朗读。
5. 部署完成后记下后端 HTTPS 地址（如 `https://xxx.railway.app`）。

### 前端（Vercel）

1. 在 Vercel 导入同一仓库，**根目录** 设为 `frontend`。
2. Build Command：`npm run build`；Output 使用 Next.js 默认。
3. **环境变量**：见下表「前端环境变量」。
4. 部署后前端会通过 rewrite 将 `/api/*` 转发到后端。

### 后端 Docker 部署（可选）

在仓库根目录或 `backend` 目录执行：

```bash
cd backend
docker build -t zerocamp-api .
docker run -p 8000:8000 -e PORT=8000 zerocamp-api
```

平台支持 Docker 时，将 **Dockerfile 路径** 设为 `backend/Dockerfile`，**构建上下文** 设为 `backend`。若 `backend/media` 未纳入镜像，可在运行时挂载卷提供媒体文件。

### 生产环境变量一览

| 位置 | 变量名 | 必填 | 说明 |
|------|--------|------|------|
| 前端 Vercel | `NEXT_PUBLIC_API_ORIGIN` | 是（生产） | 后端 API 的 HTTPS 地址 |
| 前端 Vercel | `NEXT_PUBLIC_BTC_ADDRESS` | 否 | 比特币收款地址 |
| 前端 Vercel | `NEXT_PUBLIC_TRON_ADDRESS` | 否 | TRON 钱包地址（TRX / USDT-TRC20） |
| 前端 Vercel | `NEXT_PUBLIC_ADSENSE_CLIENT_ID` / `NEXT_PUBLIC_ADSENSE_SLOT` | 否 | Google 广告 |
| 前端 Vercel | `NEXT_PUBLIC_CARBON_SERVE` / `NEXT_PUBLIC_CARBON_PLACEMENT` | 否 | Carbon Ads（支持页等） |
| 前端 Vercel | `NEXT_PUBLIC_ALT_AD_SCRIPT_URL` | 否 | 自定义广告脚本（如 Ethical Ads） |
| 后端 | `PORT` | 否 | 平台注入，默认 8000 |
| 后端 | `MINIMAX_API_KEY` / `MINIMAX_GROUP_ID` | 否 | TTS，不设则回退浏览器朗读 |

广告位与比特币收款说明见 [docs/monetization.md](docs/monetization.md)。
