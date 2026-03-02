# Manim 视频渲染与 LaTeX

## 渲染 MP4（无需 LaTeX）

```bash
pip install -r scripts/requirements-manim.txt   # 或 python3 -m pip install manim
python3 scripts/render_manim_videos.py
```

生成的 `vid1.mp4`、`vid2.mp4` 会复制到 `backend/media/videos/`，前端请求 `/api/media/video/vid1` 即可播放。

## 使用 LaTeX 显示数轴数字（可选）

Manim 在 `NumberLine(..., include_numbers=True)` 时会调用系统 **LaTeX** 渲染数字。若未安装 LaTeX，会报错 `FileNotFoundError: latex`。

**macOS 安装 LaTeX（二选一）：**

1. **BasicTeX（约 100MB，推荐）**
   ```bash
   brew install --cask basictex
   ```
   安装后**重启终端**或执行：
   ```bash
   eval "$(/usr/libexec/path_helper)"
   ```
   然后可用 `latex -version` 检查。

2. **MacTeX 完整版（约 4GB）**
   ```bash
   brew install --cask mactex
   ```

安装完成后重新运行 `python3 scripts/render_manim_videos.py`，vid1 的时间轴会显示 0–6 数字。
