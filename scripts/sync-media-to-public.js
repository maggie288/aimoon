#!/usr/bin/env node
/**
 * 将 backend/media/images 中的图片复制到 frontend/public/images，
 * 并重新生成 manifest.json，供 Vercel CDN 图片使用。
 * 用法：从项目根目录执行 node scripts/sync-media-to-public.js
 */
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const srcDir = path.join(root, "backend", "media", "images");
const destDir = path.join(root, "frontend", "public", "images");
const extOrder = [".svg", ".webp", ".png", ".jpg", ".jpeg"];

if (!fs.existsSync(srcDir)) {
  console.warn("backend/media/images 不存在，跳过复制");
  process.exit(0);
}

if (!fs.existsSync(destDir)) fs.mkdirSync(destDir, { recursive: true });

let copied = 0;
fs.readdirSync(srcDir).forEach((f) => {
  if (f === "manifest.json") return;
  const src = path.join(srcDir, f);
  if (!fs.statSync(src).isFile()) return;
  const dest = path.join(destDir, f);
  if (!fs.existsSync(dest) || fs.statSync(src).mtimeMs > fs.statSync(dest).mtimeMs) {
    fs.copyFileSync(src, dest);
    copied++;
  }
});
if (copied) console.log("已复制", copied, "个文件到 frontend/public/images");

const map = {};
fs.readdirSync(destDir).forEach((f) => {
  if (f === "manifest.json" || f === "placeholder.svg") return;
  const ext = path.extname(f).toLowerCase();
  const base = path.basename(f, ext);
  const idx = extOrder.indexOf(ext);
  if (idx === -1) return;
  if (!(base in map) || extOrder.indexOf(path.extname(map[base]).toLowerCase()) > idx) {
    map[base] = f;
  }
});
fs.writeFileSync(path.join(destDir, "manifest.json"), JSON.stringify(map, null, 0));
console.log("已更新 manifest.json，共", Object.keys(map).length, "个媒体 ID");
