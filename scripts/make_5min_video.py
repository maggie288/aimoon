#!/usr/bin/env python3
"""
根据第一至三集故事生成约 5 分钟 MP4 视频：旁白（edge-tts）+ 项目图片 + ffmpeg 合成。
依赖：pip install edge-tts；系统需安装 ffmpeg。
输出：backend/media/zerocamp_5min.mp4
"""
import asyncio
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
MEDIA = BACKEND / "media"
IMAGE_DIR = MEDIA / "images"
OUT_VIDEO = MEDIA / "zerocamp_5min.mp4"
VOICE = "zh-CN-XiaoyiNeural"  # 女声旁白

# 分镜：每段 (旁白文本, 对应图片 media_id)。总旁白约 5 分钟（约 300 秒）。
SCENES = [
    ("月球生存三十天，零号营地。这是一个关于三个人在月球南极沙克尔顿边缘、建立临时家园的故事。第一集，第一缕光。", "img2"),
    ("登陆舱在沙克尔顿陨石坑边缘着陆。一边是永昼峰的刺眼阳光，一边是无边的黑。没有明天早上可以等，只有我们能不能撑过这一夜。接下来六小时，他们只做三件事：检漏、保电保热、和地球连上线。", "img3"),
    ("跟时间赛跑，跟漏气赛跑，跟电量赛跑。六小时粗算至少要十二千瓦时。电池有，但那是按很快接上太阳算的。要是接不上呢？就得关东西。关什么、留什么，得事先想好，不能落地再吵。", "img3"),
    ("漏了，什么都没意义。月表跟空间站不一样；站上漏了还能躲到别的舱，月球上就这一层皮。所以六小时里，检漏是头等，而且别开门。一开门月尘进来，那东西又细又带静电，专门毁密封圈。", "img6"),
    ("压力随时间往下走，漏得越快、掉得越快。检漏不是在找有没有洞，是在确认漏得够不够慢——慢到六小时内我们安全。那三个人盯着压力曲线的时候，其实是在等一个答案：我们是安全的，还是正在漏。", "img20"),
    ("密封稳了，下一关是电和热。生命维持、压力监测、最小通信——这些不能关。科学仪器、机械臂、多余照明——能关就关。省下来的电和热，就是多撑一会儿的资本。清单上写可关就是可关，必留就是必留。", "img7"),
    ("月表阴影区可以到零下一百七十几度。舱体一侧烤着太阳，一侧对着宇宙冷库。加热与散热必须平衡，否则舱温会持续升或降。那六小时要确认：加热器够不够、电池撑不撑得住。", "img19"),
    ("第三关才是通信。目标很简单：至少有一次成功上行，心跳加关键遥测。有中继就实时传，没有就先存着，等过顶再补。地面只要收到一次，就知道人还在、舱还好。", "img9"),
    ("连上了。我们和地球重新连上了。那句话要是由指挥官亲口说出来，对舱里三个人会很有分量。不是给地面听的，是给他们自己听的：我们又在一个被听见的世界里了。", "img13"),
    ("第二集，能量之源。昨天那六小时他们撑过来了，舱是密封的，心跳也发出去了。今天天亮，第一件事就是展开太阳能板。设计值八十五千瓦峰值，沙克尔顿永昼峰边上理论日照够。但今早传回来的数据不对。", "img14"),
    ("理论峰值应该在八十千瓦量级，日均发电约四十五千瓦时。但实测只有设计值的百分之六十七。月尘沉积让透光率掉了大约十二；温度效应又掉了八；还有安装角度和局部阴影，再掉十三。不是设备坏了，是环境比我们乐观估计的狠。", "img17"),
    ("他们要学会在不够用的光里把日子过下去。从今天起所有规划按百分之六十七有效功率算。我们知道电从哪来、够不够用——不是乐观，是心里有数。", "img18"),
    ("第三集，呼吸之间。呼吸——我们在地球上从不用想的事，在舱里变成一串数字和阀门。三个人、一个月球日，氧和二氧化碳的账都要跟电绑在一起。电解水制氧、二氧化碳清除、舱内分压稳定。", "img21"),
    ("成人静息耗氧，三个人一天大约零点八四公斤氧。电解每公斤氧要耗电五度半。所以光制氧这一项，三人一天就要约四度六，占六十七功率下一日发电量的一成多。他们每吸一口气，背后是电在烧。", "img21"),
    ("他们第一次盯着氧分压和二氧化碳曲线的时候会想：我们吸的每一口气，都在这上面。绿区不是完美，是安全。二氧化碳进黄区就要加大清除或切备用罐，不能拖到红区。", "img22"),
    ("第一次危机不是爆炸，是某个曲线慢慢往上爬。下午二氧化碳缓慢升到零点三五，清除率略低于产生率。他们按预案切换吸附罐、加大风机，半小时后曲线回落。我们按预案做了，我们把这口气接上了。", "img23"),
    ("零号营地，前三日。第一缕光、能量之源、呼吸之间。没有插旗，没有豪言，只有不漏的舱、够用的电、连上的线。我们还在，我们听得见彼此。明天见。", "img24"),
]


def normalize_tts(t: str) -> str:
    return t.replace("₂", "2").replace("₁", "1").replace("₀", "0").replace("→", "到").replace("↑", "升").replace("≤", "<=").replace("≥", ">=")


async def tts_save(text: str, out_path: Path) -> bool:
    import edge_tts
    text = normalize_tts(text)
    try:
        comm = edge_tts.Communicate(text, VOICE, rate="-2%")
        await comm.save(str(out_path))
        return out_path.stat().st_size > 0
    except Exception as e:
        print(f"  TTS error: {e}", file=sys.stderr)
        return False


def get_audio_duration_sec(mp3_path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(mp3_path)],
        capture_output=True, text=True, check=False, timeout=5
    )
    if out.returncode != 0 or not out.stdout.strip():
        return 15.0
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 15.0


def make_segment_video(image_path: Path, audio_path: Path, duration: float, out_path: Path, width: int = 1280, height: int = 720) -> bool:
    """生成单段：图片 + 音频，长度以音频为准。"""
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(image_path),
        "-i", str(audio_path),
        "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264", "-t", str(duration), "-shortest",
        "-c:a", "aac", "-b:a", "128k", "-pix_fmt", "yuv420p",
        "-r", "24",
        str(out_path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print(r.stderr[-800:] if r.stderr else "ffmpeg failed", file=sys.stderr)
        return False
    return True


def concat_videos(seg_paths: list[Path], out_path: Path) -> bool:
    list_file = out_path.parent / "concat_list.txt"
    with open(list_file, "w") as f:
        for p in seg_paths:
            f.write(f"file '{p.absolute()}'\n")
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(out_path)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print(r.stderr[-800:] if r.stderr else "concat failed", file=sys.stderr)
        return False
    list_file.unlink(missing_ok=True)
    return True


async def main():
    work_dir = MEDIA / "video_5min_work"
    work_dir.mkdir(parents=True, exist_ok=True)
    audio_dir = work_dir / "audio"
    video_dir = work_dir / "segments"
    audio_dir.mkdir(exist_ok=True)
    video_dir.mkdir(exist_ok=True)

    # 1) 生成每段 TTS
    print("Generating TTS for", len(SCENES), "segments...")
    for i, (text, _) in enumerate(SCENES):
        mp3 = audio_dir / f"seg_{i:02d}.mp3"
        if not await tts_save(text, mp3):
            sys.exit(1)
        print(f"  {mp3.name} ok")

    # 2) 每段时长
    durations = []
    for i in range(len(SCENES)):
        mp3 = audio_dir / f"seg_{i:02d}.mp3"
        d = get_audio_duration_sec(mp3)
        durations.append(d)
    total_sec = sum(durations)
    print(f"Total audio: {total_sec:.1f}s ({total_sec/60:.1f} min)")

    # 3) 每段视频：图片 + 对应音频
    seg_videos = []
    for i, ((_, media_id), dur) in enumerate(zip(SCENES, durations)):
        img = IMAGE_DIR / f"{media_id}.png"
        if not img.exists():
            img = IMAGE_DIR / "img2.png"  # fallback
        if not img.exists():
            print(f"Missing image for {media_id}, skip segment {i}", file=sys.stderr)
            continue
        aud = audio_dir / f"seg_{i:02d}.mp3"
        out_seg = video_dir / f"seg_{i:02d}.mp4"
        print(f"  Encoding segment {i}: {media_id} ({dur:.1f}s)...")
        if not make_segment_video(img, aud, dur, out_seg):
            sys.exit(1)
        seg_videos.append(out_seg)

    # 4) 拼接
    print("Concatenating to", OUT_VIDEO)
    if not concat_videos(seg_videos, OUT_VIDEO):
        sys.exit(1)
    print("Done:", OUT_VIDEO)
    return 0


if __name__ == "__main__":
    try:
        import edge_tts  # noqa: F401
    except ImportError:
        print("Install: pip install edge-tts", file=sys.stderr)
        sys.exit(1)
    sys.exit(asyncio.run(main()))
