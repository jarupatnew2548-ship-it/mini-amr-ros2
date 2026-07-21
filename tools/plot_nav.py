#!/usr/bin/env python3
"""
Render Task-11 navigation deliverables from a recorded run (nav_demo_recorder
JSON): an RViz-style still of the map + planned global path + executed
trajectory + goal, a 'map + initial pose' still, and an animated GIF of the
robot driving to the goal.
"""
import json
import math
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrow
from matplotlib.animation import FuncAnimation, PillowWriter

JSON = "/tmp/nav_demo.json"
OUT = "/home/nj/amr_ws/deliverables"
os.makedirs(OUT, exist_ok=True)

d = json.load(open(JSON))
m = d["map"]
W, H, res = m["width"], m["height"], m["resolution"]
ox, oy = m["origin"]
grid = np.array(m["data"], dtype=np.int16).reshape(H, W)

# world extent for imshow
extent = [ox, ox + W * res, oy, oy + H * res]

# RViz-like map colours: unknown grey, free light, occupied black
img = np.empty((H, W, 3), dtype=np.uint8)
img[grid < 0] = (120, 120, 120)          # unknown
img[(grid >= 0) & (grid < 65)] = (240, 240, 240)  # free
img[grid >= 65] = (20, 20, 20)           # occupied

plan = np.array(d["plan"]) if d["plan"] else np.zeros((0, 2))
traj = np.array([[p[1], p[2]] for p in d["trajectory"]])
yaws = [p[3] for p in d["trajectory"]]
start = d["init_pose"]
goal = d["goal_pose"]
succeeded = d["succeeded"]
goal_err = math.hypot(traj[-1, 0] - goal[0], traj[-1, 1] - goal[1]) if len(traj) else 0.0

BG = "#2b2b2b"
FG = "#e8e8e8"


def base_axes(title):
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.imshow(img, extent=extent, origin="lower", interpolation="nearest")
    ax.set_xlim(-1.9, 1.9)
    ax.set_ylim(-1.9, 1.9)
    ax.set_xlabel("x  [m]  (map frame)", color=FG)
    ax.set_ylabel("y  [m]  (map frame)", color=FG)
    ax.set_title(title, color=FG, fontsize=13, weight="bold")
    ax.tick_params(colors=FG)
    for s in ax.spines.values():
        s.set_color("#666")
    ax.grid(True, color="#444", lw=0.5)
    return fig, ax


def draw_robot(ax, x, y, yaw, color="#25c2f2"):
    ax.add_patch(plt.Circle((x, y), 0.11, color=color, zorder=6))
    ax.add_patch(FancyArrow(x, y, 0.22 * math.cos(yaw), 0.22 * math.sin(yaw),
                            width=0.03, head_width=0.11, head_length=0.09,
                            color=color, zorder=7, length_includes_head=True))


# ---------------------------------------------------------------- still #1
# map + initial robot pose + goal marker (state before navigating)
fig, ax = base_axes("Nav2 map-based navigation  -  map loaded + initial pose")
draw_robot(ax, start[0], start[1], start[2])
ax.plot(goal[0], goal[1], marker="*", ms=22, color="#ff4d4d",
        markeredgecolor="k", zorder=8)
ax.annotate("goal", (goal[0], goal[1]), color="#ff4d4d",
            xytext=(8, 8), textcoords="offset points", weight="bold")
ax.annotate("robot\n(AMCL pose)", (start[0], start[1]), color="#25c2f2",
            xytext=(-46, -34), textcoords="offset points", weight="bold")
ax.legend(handles=[
    plt.Line2D([], [], marker="o", ls="", color="#25c2f2", label="robot pose"),
    plt.Line2D([], [], marker="*", ls="", color="#ff4d4d", label="goal pose"),
    plt.Line2D([], [], marker="s", ls="", color="#f0f0f0", label="free (map)"),
    plt.Line2D([], [], marker="s", ls="", color="#787878", label="unknown"),
], loc="upper left", facecolor="#1c1c1c", labelcolor=FG, framealpha=0.9)
fig.tight_layout()
fig.savefig(f"{OUT}/rviz_map_pose.png", dpi=130, facecolor=BG)
plt.close(fig)

# ---------------------------------------------------------------- still #2
# map + planned global path + executed trajectory + goal reached
fig, ax = base_axes("Nav2 map-based navigation  -  global path + goal reached")
if len(plan):
    ax.plot(plan[:, 0], plan[:, 1], "-", color="#39ff14", lw=3.0,
            zorder=4, label="global path (/plan)")
if len(traj):
    ax.plot(traj[:, 0], traj[:, 1], "--", color="#ffb000", lw=2.2,
            zorder=5, label="executed trajectory")
draw_robot(ax, traj[-1, 0], traj[-1, 1], yaws[-1])
ax.plot(start[0], start[1], "o", ms=10, color="#25c2f2",
        markeredgecolor="k", zorder=6)
ax.plot(goal[0], goal[1], marker="*", ms=22, color="#ff4d4d",
        markeredgecolor="k", zorder=8)
ax.annotate("start", (start[0], start[1]), color="#25c2f2",
            xytext=(-40, -28), textcoords="offset points", weight="bold")
ax.annotate("goal", (goal[0], goal[1]), color="#ff4d4d",
            xytext=(10, 6), textcoords="offset points", weight="bold")
status = "GOAL REACHED" if succeeded else "FAILED"
ax.text(0.98, 0.02,
        f"{status}   (final error {goal_err*100:.1f} cm,  {len(plan)}-pose path)",
        transform=ax.transAxes, ha="right", va="bottom", color="#39ff14",
        weight="bold", fontsize=11,
        bbox=dict(boxstyle="round", fc="#1c1c1c", ec="#39ff14"))
ax.legend(loc="upper left", facecolor="#1c1c1c", labelcolor=FG, framealpha=0.9)
fig.tight_layout()
fig.savefig(f"{OUT}/rviz_map_path.png", dpi=130, facecolor=BG)
# keep a copy under the descriptive analysis name too
fig.savefig(f"{OUT}/map_path_plot.png", dpi=130, facecolor=BG)
plt.close(fig)

# ---------------------------------------------------------------- GIF
fig, ax = base_axes("Nav2 map-based navigation  -  driving to goal")
if len(plan):
    ax.plot(plan[:, 0], plan[:, 1], "-", color="#39ff14", lw=2.5, zorder=3)
ax.plot(goal[0], goal[1], marker="*", ms=20, color="#ff4d4d",
        markeredgecolor="k", zorder=8)
trail, = ax.plot([], [], "--", color="#ffb000", lw=2.0, zorder=4)
robot_dot = plt.Circle((start[0], start[1]), 0.11, color="#25c2f2", zorder=6)
ax.add_patch(robot_dot)
heading = ax.plot([], [], "-", color="#25c2f2", lw=3, zorder=7)[0]
status_txt = ax.text(0.98, 0.02, "", transform=ax.transAxes, ha="right",
                     va="bottom", color="#39ff14", weight="bold", fontsize=11,
                     bbox=dict(boxstyle="round", fc="#1c1c1c", ec="#39ff14"))

step = max(1, len(traj) // 60)
frames = list(range(0, len(traj), step)) + [len(traj) - 1] * 8


def update(i):
    x, y = traj[i, 0], traj[i, 1]
    yaw = yaws[i]
    trail.set_data(traj[:i + 1, 0], traj[:i + 1, 1])
    robot_dot.center = (x, y)
    heading.set_data([x, x + 0.25 * math.cos(yaw)], [y, y + 0.25 * math.sin(yaw)])
    err = math.hypot(x - goal[0], y - goal[1])
    if i >= len(traj) - 1 and succeeded:
        status_txt.set_text(f"GOAL REACHED  ({err*100:.1f} cm)")
    else:
        status_txt.set_text(f"navigating...  dist to goal {err:.2f} m")
    return trail, robot_dot, heading, status_txt


anim = FuncAnimation(fig, update, frames=frames, blit=True)
anim.save(f"{OUT}/navigation.gif", writer=PillowWriter(fps=12), dpi=90)
plt.close(fig)

print("wrote:")
for f in ("rviz_map_pose.png", "rviz_map_path.png", "map_path_plot.png",
          "navigation.gif"):
    p = f"{OUT}/{f}"
    print(f"  {p}  ({os.path.getsize(p)} bytes)")
