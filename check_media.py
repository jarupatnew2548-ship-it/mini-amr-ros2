import subprocess, re
import imageio_ffmpeg
from PIL import Image
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
D = "/home/nj/amr_ws/deliverables"

for f in ("clip_robot.mp4", "clip_safety.mp4", "clip_slam.mp4", "clip_nav.mp4", "mini_amr_final_demo.mp4"):
    p = f"{D}/{f}"
    probe = subprocess.run([ffmpeg, "-i", p], stderr=subprocess.PIPE, text=True)
    m = re.search(r"(\d{3,5})x(\d{3,5})", probe.stderr)
    if m:
        w, h = int(m.group(1)), int(m.group(2))
        print(f"{f:28s} {w}x{h}  aspect={w/h:.4f}")

for f in ("title_hero_new.png", "nav_goal_new.png", "poster_robot.png", "poster_safety.png", "poster_slam.png", "poster_nav.png"):
    im = Image.open(f"{D}/{f}")
    print(f"{f:28s} {im.size[0]}x{im.size[1]}  aspect={im.size[0]/im.size[1]:.4f}")
