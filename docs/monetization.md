# 零号营地 · 变现说明

## 一、广告位（浏览与点击收益）

本站已预留多处广告位，支持多种广告来源，可只挂一种或组合使用。

### 位置与来源

| 位置 | 默认来源 | 说明 |
|------|----------|------|
| 首页 · 标题下横条 | Google | 设置 AdSense 后展示 |
| 首页 · 页脚上矩形 | Google | 同上 |
| 剧集页 · 顶栏下横条 | Google | 同上 |
| 支持页 · 标题下矩形 | **Carbon Ads** | 设置 Carbon 后展示，偏开发者/科技；与 Google 不同页可同时用 |

在代码里可给任意 `<AdSlot>` 指定 `provider="google"`、`provider="carbon"` 或 `provider="custom"`，对应不同环境变量。

### 1. Google AdSense

1. 注册 [Google AdSense](https://www.google.com/adsense)，通过审核后获得 **发布商 ID**（形如 `ca-pub-xxxxxxxxxxxxxxxx`）。
2. 在 AdSense 后台创建 **广告单元**，得到 **广告位 ID**（一串数字）。
3. 在 Vercel 或本地 `.env` 中配置：
   - `NEXT_PUBLIC_ADSENSE_CLIENT_ID=ca-pub-xxxxxxxxxxxxxxxx`
   - `NEXT_PUBLIC_ADSENSE_SLOT=你的广告位ID`
4. 未配置时对应广告位显示占位「Ad」。收益与访问量、点击率相关。

### 2. Carbon Ads

面向开发者/科技站点，隐私友好、无追踪。与 Google 可同时使用（不同广告位）。

1. 申请 [Carbon Ads](https://www.carbonads.net)，通过后获得 **serve** 与 **placement**。
2. 配置环境变量：
   - `NEXT_PUBLIC_CARBON_SERVE=你的 serve code`
   - `NEXT_PUBLIC_CARBON_PLACEMENT=你的 placement`（一般用站点名或域名）
3. 支持页的矩形位已设为 Carbon；其他页面可在对应组件上写 `provider="carbon"` 使用 Carbon。

注意：Carbon 要求 **同一页** 不能出现其他广告网络，因此支持页仅用 Carbon；首页、剧集页用 Google。

### 3. 自定义广告脚本（Ethical Ads、Media.net 等）

任一广告网络只要提供「一段脚本 URL」，都可以用「自定义」方式挂上。

1. 在后台拿到广告脚本的 **URL**（例如 `https://.../publisher/xxx.js`）。
2. 配置环境变量：
   - `NEXT_PUBLIC_ALT_AD_SCRIPT_URL=该脚本的完整 URL`
3. 在需要的位置使用 `<AdSlot provider="custom" />`，页面会加载该脚本；脚本通常会往 `#alt-ad-slot` 或页面里插入广告。若对方要求固定容器 id，可把我们的容器 id 告诉他们（当前为 `alt-ad-slot`）。

**Ethical Ads**（[ethicalads.io](https://www.ethicalads.io)）：隐私优先、无追踪，申请通过后按说明拿到脚本 URL，用上述自定义方式即可。

---

## 二、加密货币收款（比特币 / TRON）

本站支持页支持两种方式，可只设一种或两种都设：

- **比特币 (BTC)**：环境变量 **`NEXT_PUBLIC_BTC_ADDRESS`**，支持页显示地址 + `bitcoin:` 二维码。
- **TRON (TRX / USDT-TRC20)**：环境变量 **`NEXT_PUBLIC_TRON_ADDRESS`**，支持页显示你的 TRON 钱包地址 + 二维码，支持者可直接转 TRX 或 USDT（TRC20）到此地址。

你从自己的钱包收款，无平台抽成。

### 地址从哪里获取？

**这两个地址都是「你自己的钱包收款地址」**，从你使用的钱包里复制，不是从 Vercel 或本站生成的。

1. **比特币 (BTC)**  
   用**比特币钱包**（不是 TRON 钱包）：在「收款 / 接收」里看到的地址，形如 `bc1q...` 或 `1...`、`3...`。复制后填到 Vercel 的 `NEXT_PUBLIC_BTC_ADDRESS`。

2. **TRON（你现在的钱包）**  
   你的钱包是 **TRON** 的话，那串以 **T 开头**的地址就是 TRON 地址（例如 `TXYZ...`）。在 TRON 钱包 App 里找到「收款 / 接收」，复制该地址，填到 Vercel 的 **`NEXT_PUBLIC_TRON_ADDRESS`** 即可。支持者可以往这个地址转 **TRX** 或 **USDT（TRC20）**，你用自己的 TRON 钱包就能收到。  
   **注意**：TRON 和比特币是不同链，TRON 地址不能当比特币地址用；比特币地址也不能当 TRON 地址用。你只有 TRON 钱包就只设 `NEXT_PUBLIC_TRON_ADDRESS`。

3. **在 Vercel 里填写**  
   项目 → Settings → Environment Variables → 新建变量：  
   - 若用 TRON：名称 `NEXT_PUBLIC_TRON_ADDRESS`，值 = 你复制的 TRON 地址（T 开头）。  
   - 若用比特币：名称 `NEXT_PUBLIC_BTC_ADDRESS`，值 = 你复制的 BTC 地址。  
   保存后重新部署，支持页会显示对应地址和二维码。
