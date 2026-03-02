#!/usr/bin/env python3
"""
Render Manim scenes and copy MP4 to backend/media/videos/ for serving.
Requires: pip install manim (manim community)
Run from repo root: python scripts/render_manim_videos.py
"""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCENES_DIR = REPO_ROOT / "scripts" / "manim_scenes"
OUT_DIR = REPO_ROOT / "backend" / "media" / "videos"
# Map media_id -> (scene_file_basename, SceneClass name)
VIDEO_SCENES = {
    "vid1": ("zerocamp_scenes", "PressureDecay"),
    "vid2": ("zerocamp_scenes", "ThermalBalance"),
    "vid3": ("zerocamp_scenes", "SolarPowerCurve"),
}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    scene_file = SCENES_DIR / "zerocamp_scenes.py"
    if not scene_file.exists():
        print("Scene file not found:", scene_file)
        sys.exit(1)

    # Render with manim: -pql = preview, low quality, render to mp4
    # Output: media/videos/zerocamp_scenes/480p60/PressureDecay.mp4 etc.
    for media_id, (module, scene_name) in VIDEO_SCENES.items():
        print(f"Rendering {media_id} -> {scene_name}...")
        try:
            subprocess.run(
                [
                    sys.executable, "-m", "manim",
                    "-pql",  # 480p, low quality, save last frame
                    str(scene_file),
                    scene_name,
                ],
                cwd=str(REPO_ROOT),
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            print("Manim failed:", e.stderr or e.stdout)
            sys.exit(1)
        except FileNotFoundError:
            print("Manim not found. Install with: pip install manim")
            sys.exit(1)

    # Manim writes to media/videos/<module>/<resolution>/<SceneName>.mp4 (-pql => 480p15)
    manim_media = REPO_ROOT / "media" / "videos" / "zerocamp_scenes"
    if not manim_media.exists():
        print("Manim output not found at", manim_media)
        sys.exit(1)
    # Find resolution subdir (480p15 or 480p60)
    res_dirs = list(manim_media.glob("480p*"))
    if not res_dirs:
        print("No 480p* dir in", manim_media)
        sys.exit(1)
    manim_dir = res_dirs[0]

    for media_id, (_, scene_name) in VIDEO_SCENES.items():
        src = manim_dir / f"{scene_name}.mp4"
        if src.exists():
            dst = OUT_DIR / f"{media_id}.mp4"
            import shutil
            shutil.copy2(src, dst)
            print(f"Copied {src.name} -> {dst}")
        else:
            print(f"Missing: {src}")

    print("Done. Videos in", OUT_DIR)


if __name__ == "__main__":
    main()
