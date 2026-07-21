# Task 11 — Nav2 Map-based Navigation (Mini-AMR)

## Objective
Use a previously saved map to autonomously navigate the simulated Mini-AMR to a
goal pose: load the map, start localization + Nav2, set the initial pose, send a
goal, and verify the robot **plans a path and reaches the goal**.

---

## 1. System overview

The single launch file `mini_amr_navigation/launch/navigation.launch.py` starts
everything:

| Component | Package / node | Role |
|-----------|----------------|------|
| Robot model | `robot_state_publisher` + `joint_state_publisher` | Publishes the URDF TF tree `base_footprint → base_link → {wheels, laser_link}` |
| Odometry | `mini_amr_control/fake_odom_publisher` | Integrates `/cmd_vel` → publishes `/odom` and TF `odom → base_footprint` (this is what actually drives the robot) |
| LiDAR | `mini_amr_sensors/fake_scan_publisher` (`pattern:=clear`) | Publishes an open-space `/scan` so AMCL localization stays stable |
| Map server | `nav2_map_server` | Loads the saved occupancy grid and publishes `/map` |
| Localization | `nav2_amcl` | Publishes TF `map → odom` (self-initialized at the origin) |
| Planning | `nav2_planner` (NavFn / Dijkstra) | Global path on `/plan` |
| Control | `nav2_controller` (MPPI) | Follows the path, outputs `/cmd_vel` |
| Behavior tree | `nav2_bt_navigator` | Orchestrates plan → follow → recovery, exposes the `NavigateToPose` action |
| Lifecycle | `nav2_lifecycle_manager` | Configures + activates all Nav2 nodes |
| Visualization | `rviz2` | Shows map, robot, path, goal |

**TF tree:** `map → odom → base_footprint → base_link → (wheels, laser_link)`
- `map → odom` : AMCL (localization)
- `odom → base_footprint` : fake odometry (motion)
- the rest : static, from the URDF

---

## 2. How to run

```bash
cd ~/amr_ws
colcon build
source install/setup.bash

# Full demo with RViz
ros2 launch mini_amr_navigation navigation.launch.py

# Headless (no RViz) — e.g. for recording / CI
ros2 launch mini_amr_navigation navigation.launch.py use_rviz:=false

# Use a different saved map
ros2 launch mini_amr_navigation navigation.launch.py map:=/path/to/map.yaml
```

In RViz:
1. The **map** loads automatically and AMCL self-initializes at the origin.
   (Optionally refine with the **2D Pose Estimate** tool.)
2. Send a goal with the **Nav2 Goal** tool, or from the CLI:
   ```bash
   ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
     "{pose: {header: {frame_id: map}, pose: {position: {x: 1.0, y: 0.8}, \
       orientation: {w: 1.0}}}}"
   ```
> Note: the RViz default *"2D Goal Pose"* tool only publishes to `/goal_pose`,
> which Nav2 does **not** subscribe to. Use the **Nav2 Goal** tool or the
> `navigate_to_pose` **action** to actually start navigation.

A reusable recorder node runs one full navigation and dumps the result:
```bash
ros2 run mini_amr_navigation nav_demo_recorder --ros-args -p goal_x:=1.0 -p goal_y:=0.8
```

---

## 3. The navigation process (what happens on a goal)

1. **Map load** – `map_server` publishes the static occupancy grid on `/map`
   (transient-local), which fills the global costmap's static layer.
2. **Localization** – AMCL provides `map → odom`; with the robot's odometry this
   yields the robot pose in the `map` frame.
3. **Global planning** – on a goal, `planner_server` (NavFn) searches the global
   costmap (static map + inflation) and publishes the global path on `/plan`.
4. **Local control** – the MPPI `controller_server` samples trajectories that
   follow `/plan` while respecting kinematic limits, publishing `/cmd_vel`.
5. **Motion** – `fake_odom_publisher` integrates `/cmd_vel`, moving the robot and
   updating `odom → base_footprint`.
6. **Goal check** – when the robot is within `xy_goal_tolerance` (0.12 m) of the
   goal, the goal checker reports success and the BT returns `SUCCEEDED`.

---

## 4. Key configuration decisions (and problems solved)

The base simulation was built for earlier tasks with **synthetic sensors**, which
broke a naive Nav2 setup. Each issue below was diagnosed from live logs/data and
fixed in `config/nav2_params.yaml` / the launch file:

1. **Saved map was speckle noise.** The Task-10 SLAM map was built with a *random*
   fake LiDAR, so 139 of 154 "occupied" cells were isolated noise pixels that
   blocked the planner. → Denoised it (`tools/denoise_map.py`, connected-component
   filter) into `task11_map.pgm/.yaml`, which is what navigation uses. The
   original `task10_map` is kept untouched alongside it. Both maps are installed
   with the package under `mini_amr_navigation/maps/`.
2. **Random scan flooded the costmaps.** The obstacle/voxel layers marked phantom
   obstacles everywhere. → For map-based navigation the costmaps use the **static
   map + inflation only**; inflation radius reduced 0.70 → 0.35 m (just above the
   0.22 m robot radius).
3. **AMCL drift.** With a random scan AMCL's `map → odom` random-walked ~0.5 m.
   → Added a `clear` (open-space) scan mode and lowered the motion-noise `alpha`
   values so AMCL stays locked to odometry.
4. **planner_server failed to activate.** Its activation blocked waiting for the
   `map → base_link` TF (no initial pose yet) and timed out after 60 s. → AMCL now
   `set_initial_pose: true` at the origin, so `map → odom` exists immediately and
   the whole stack activates deterministically.
5. **RViz stability.** RViz is launched *after* the stack is active (software-GL
   rendering was starving lifecycle activation), and a `joint_state_publisher`
   was added so the continuous wheel joints get TF and RobotModel renders cleanly.

---

## 5. Result

- Goal: **(x = 1.0, y = 0.8)** in the `map` frame.
- Global path planned: **61 poses** from start to goal.
- Final robot pose: **(1.01, 0.85)** → **goal error ≈ 5.5 cm** (within the 0.12 m
  tolerance).
- Behavior-tree result: **`SUCCEEDED`** (`error_code: 0`, controller log:
  *"Reached the goal!"*, bt_navigator: *"Goal succeeded"*).

The robot loads the map, localizes, plans a global path, follows it, and reaches
the goal. ✔

---

## 6. Deliverables (in `deliverables/`)

| File | What it shows |
|------|---------------|
| `rviz_map_pose.png` | **RViz2** — map loaded + robot at initial pose |
| `rviz_map_path.png` | **RViz2** — map + robot + green global path (`/plan`) to the goal |
| `navigation.gif`    | **RViz2** — short video of the robot driving to the goal |
| `map_path_plot.png` | Data plot of the real run: map + planned path + executed trajectory + *GOAL REACHED* |
| `NAVIGATION_NOTES.md` | This document |

Navigation launch file: `src/mini_amr_navigation/launch/navigation.launch.py`
Nav2 parameters: `src/mini_amr_navigation/config/nav2_params.yaml`
Saved maps: `src/mini_amr_navigation/maps/` (`task11_map` = denoised, used by default)
Reproducibility scripts: `tools/` (`denoise_map.py`, `record_nav.sh`, `plot_nav.py`)
