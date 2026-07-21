#!/usr/bin/env python3
"""
Denoise the raw SLAM map (task10_map) for Nav2 navigation.

The Task-10 map was built with a *synthetic random* LiDAR, so its occupancy
grid is peppered with isolated 'obstacle' pixels that do not correspond to any
real structure and that block the Nav2 global planner.  This removes small
occupied connected-components (speckle noise) while leaving any genuine
structure untouched, and writes a clean map next to the original.
"""
import sys
from collections import deque
from PIL import Image

from pathlib import Path

# maps live inside the navigation package (installed to its share/ dir)
MAPS = Path(__file__).resolve().parent.parent / "src" / "mini_amr_navigation" / "maps"
SRC_PGM = str(MAPS / "task10_map.pgm")
DST_PGM = str(MAPS / "task11_map.pgm")
DST_YAML = str(MAPS / "task11_map.yaml")
RES = 0.05
ORIGIN = [-2.366, -2.437, 0.0]
MIN_AREA = 6          # occupied components smaller than this are noise
OCC_PIXEL_MAX = 89    # pixel < 89  => occupied  (p = (255-px)/255 > 0.65)
FREE_PIXEL = 254      # value written for cleared / free cells

img = Image.open(SRC_PGM).convert("L")
W, H = img.size
px = list(img.getdata())


def idx(x, y):
    return y * W + x


occ = [1 if v < OCC_PIXEL_MAX else 0 for v in px]
total_occ = sum(occ)

# label 8-connected occupied components
lab = [-1] * (W * H)
removed = 0
kept = 0
comp_id = 0
for y in range(H):
    for x in range(W):
        if occ[idx(x, y)] and lab[idx(x, y)] == -1:
            # BFS component
            cells = []
            q = deque([(x, y)])
            lab[idx(x, y)] = comp_id
            while q:
                cx, cy = q.popleft()
                cells.append((cx, cy))
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < W and 0 <= ny < H and occ[idx(nx, ny)] \
                                and lab[idx(nx, ny)] == -1:
                            lab[idx(nx, ny)] = comp_id
                            q.append((nx, ny))
            if len(cells) < MIN_AREA:
                for cx, cy in cells:
                    px[idx(cx, cy)] = FREE_PIXEL   # clear noise -> free
                removed += len(cells)
            else:
                kept += len(cells)
            comp_id += 1

print(f"map {W}x{H}  occupied={total_occ}  removed_noise={removed}  kept={kept}")

out = Image.new("L", (W, H))
out.putdata(px)
out.save(DST_PGM)

with open(DST_YAML, "w") as f:
    f.write(f"image: {DST_PGM.split('/')[-1]}\n")
    f.write("mode: trinary\n")
    f.write(f"resolution: {RES}\n")
    f.write(f"origin: [{ORIGIN[0]}, {ORIGIN[1]}, {ORIGIN[2]}]\n")
    f.write("negate: 0\n")
    f.write("occupied_thresh: 0.65\n")
    f.write("free_thresh: 0.196\n")

print("wrote", DST_PGM, "and", DST_YAML)
