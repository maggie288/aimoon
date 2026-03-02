# 零号营地 · 部署说明（Vercel + Railway / Render）

本文按步骤说明如何把前端部署到 **Vercel**、后端部署到 **Railway** 或 **Render**，并让前后端连通。

---

## 前置条件

- 代码已推送到 **GitHub**（仓库为 public 或已授权给 Vercel / Railway / Render）。
- 已注册 [Vercel](https://vercel.com)、[Railway](https://railway.app)、[Render](https://render.com) 账号（均支持免费额度）。

**建议顺序**：先部署后端 → 拿到后端 HTTPS 地址 → 再部署前端并填该地址，这样一次配置即可生效。

---

## 一、后端部署

后端任选 **Railway** 或 **Render** 其一即可。

### 方案 A：Railway

1. **创建项目**
   - 登录 [Railway](https://railway.app) → **New Project**。
   - 选 **Deploy from GitHub repo**，授权并选择本仓库（如 `yourname/fouragent_moon`）。

2. **指定根目录与启动**
   - 在项目里会有一个 Service（服务）。点进该 Service。
   - **Settings** → **Root Directory** 填：`backend`（只部署 backend 目录）。
   - **Settings** → **Build**：Railway 若未自动识别，可留空或 **Build Command** 留空（不构建，直接运行）。
   - **Settings** → **Deploy** → **Start Command** 填：
     ```bash
     uvicorn main:app --host 0.0.0.0 --port $PORT
     ```
     或使用项目内脚本：
     ```bash
     sh run.sh
     ```
   - Railway 会自动注入 `PORT`，无需在环境变量里再设。

3. **环境变量（可选）**
   - **Variables** 里可添加：
     - `MINIMAX_API_KEY`、`MINIMAX_GROUP_ID`（若用 MiniMax TTS）；无则前端回退浏览器朗读。
   - 不需要手动设 `PORT`。

4. **拿到后端地址**
   - **Settings** → **Networking** → **Generate Domain**，得到类似 `https://xxx.up.railway.app` 的地址。
   - 复制该 **HTTPS 地址**，后面在 Vercel 里会用到（不要带末尾斜杠）。

5. **验证**
   - 浏览器打开 `https://你的域名/api/health`，应返回 `{"status":"ok","service":"zerocamp-api"}`。

---

### 方案 B：Render

1. **创建 Web Service**
   - 登录 [Render](https://render.com) → **Dashboard** → **New +** → **Web Service**。
   - **Connect a repository**：选 GitHub 并授权，再选本仓库。

2. **配置服务**
   - **Name**：随意，如 `zerocamp-api`。
   - **Region**：选离你或目标用户近的。
   - **Root Directory** 填：`backend`。
   - **Runtime**：`Python 3`。
   - **Build Command**（可选）：若只用默认依赖可留空，或填：
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command** 填：
     ```bash
     uvicorn main:app --host 0.0.0.0 --port $PORT
     ```
     或：
     ```bash
     sh run.sh
     ```
   - Render 会自动设置 `PORT`。

3. **环境变量（可选）**
   - **Environment** 里添加：
     - `MINIMAX_API_KEY`、`MINIMAX_GROUP_ID`（若用 TTS）。

4. **拿到后端地址**
   - 创建完成后，Render 会分配一个 URL，如 `https://zerocamp-api.onrender.com`。
   - 复制该 **HTTPS 地址**（不要带末尾斜杠），用于 Vercel。

5. **验证**
   - 打开 `https://你的域名/api/health`，应返回 `{"status":"ok","service":"zerocamp-api"}`。

---

### 使用 Docker 部署后端（Railway / Render 均支持）

若希望用 Docker 构建：

- **Railway**：在 Service 的 **Settings** 里可启用 Docker，并设置 **Dockerfile Path** 为 `backend/Dockerfile`，**Docker Build Context** 为 `backend`（或仓库根目录时写 `./backend`）。无需再填 Start Command，镜像内已包含。
- **Render**：**New +** → **Web Service**，连仓库后，在 **Docker** 相关选项里指定 **Dockerfile Path** 为 `backend/Dockerfile`，构建上下文为 `backend`。

---

## 二、前端部署（Vercel）

1. **导入项目**
   - 登录 [Vercel](https://vercel.com) → **Add New** → **Project**。
   - 从 **Import Git Repository** 选择本仓库并导入。

2. **配置构建设置**
   - **Root Directory**：点击 **Edit**，改为 `frontend`（只部署前端）。
   - **Framework Preset**：应自动识别为 Next.js。
   - **Build Command**：`npm run build`（默认即可）。
   - **Output Directory**：Next.js 默认，无需改。
   - **Install Command**：`npm install`（默认即可）。

3. **环境变量（必填一项）**
   - 在 **Environment Variables** 里添加：
     - **Name**：`NEXT_PUBLIC_API_ORIGIN`
     - **Value**：上一步得到的**后端 HTTPS 地址**（如 `https://xxx.up.railway.app` 或 `https://zerocamp-api.onrender.com`），不要加末尾斜杠，不要带 `/api`。
   - 这样前端的 `/api/*` 请求会通过 Next 的 rewrite 转发到该后端。

4. **可选环境变量（按需）**
   - `NEXT_PUBLIC_BTC_ADDRESS` — 比特币收款地址。
   - `NEXT_PUBLIC_TRON_ADDRESS` — TRON 钱包地址。
   - `NEXT_PUBLIC_ADSENSE_CLIENT_ID`、`NEXT_PUBLIC_ADSENSE_SLOT` — Google 广告。
   - `NEXT_PUBLIC_CARBON_SERVE`、`NEXT_PUBLIC_CARBON_PLACEMENT` — Carbon Ads。
   - `NEXT_PUBLIC_ALT_AD_SCRIPT_URL` — 自定义广告脚本。

5. **部署**
   - 点击 **Deploy**，等待构建完成。
   - 部署成功后 Vercel 会给出一个地址，如 `https://xxx.vercel.app`。

6. **验证**
   - 打开该地址，应能打开首页。
   - 点击某一集进入剧集页，若数据与语音正常加载，说明前端已正确连到后端。

---

## 三、部署后检查清单

| 步骤 | 说明 |
|------|------|
| 后端健康检查 | 浏览器访问 `https://你的后端域名/api/health`，应返回 JSON。 |
| 前端首页 | 打开 Vercel 给的域名，能看到 30 天话题列表。 |
| 剧集页 | 点进某一天，对话与媒体能加载（依赖后端）。 |
| 支持页 | `/support` 能打开；若已设 TRON/BTC 地址，应显示对应二维码。 |
| 语言与广告 | 默认英文、可切中文；若配置了广告 env，对应位置会显示广告或占位。 |

---

## 四、自定义域名（可选）

- **Vercel**：项目 → **Settings** → **Domains** → 添加你的域名，按提示在 DNS 里添加 CNAME 或 A 记录。
- **Railway**：Service → **Settings** → **Networking** → **Custom Domain**。
- **Render**：Web Service → **Settings** → **Custom Domains**。

若前端、后端都绑了自定义域名，需把 Vercel 里的 `NEXT_PUBLIC_API_ORIGIN` 改为你的**后端自定义域名**（HTTPS），并重新部署前端。

---

## 五、常见问题

**Q：前端打开后接口 404 或报错**  
- 确认 `NEXT_PUBLIC_API_ORIGIN` 填的是后端**根地址**（如 `https://xxx.railway.app`），没有 `/api` 或末尾斜杠。
- 确认后端已成功部署且 `/api/health` 可访问。
- 修改环境变量后要在 Vercel 里 **Redeploy** 一次才会生效。

**Q：后端部署失败**  
- 检查 **Root Directory** 是否为 `backend`。
- 检查 **Start Command** 是否为 `uvicorn main:app --host 0.0.0.0 --port $PORT` 或 `sh run.sh`。
- 查看平台提供的构建/运行日志，根据报错排查依赖或路径。

**Q：Render 免费实例会休眠**  
- Render 免费版一段时间无访问会休眠，首次访问可能较慢；如需常驻可升级或改用 Railway 等。

---

更多环境变量说明见 [README 生产环境变量一览](../README.md#生产环境变量一览)，变现与收款见 [monetization.md](monetization.md)。
