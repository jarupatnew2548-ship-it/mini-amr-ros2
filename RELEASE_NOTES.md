# Release Notes — Mini-AMR ROS 2

**Platform:** ROS 2 Jazzy Jalisco · Ubuntu 24.04.4 LTS (WSL2) · Python 3.12

---

## v1.1.0 — Presentation deck & refreshed demo media

- Added `deliverables/ROS2_MiniAMR_Presentation.pptx` — a 10-slide deck with
  embedded, per-stage demo video clips and speaker notes.
- Re-recorded all demo clips (`clip_robot`, `clip_safety`, `clip_slam`,
  `clip_nav`) from live ROS 2 / RViz2 sessions at native window resolution,
  with the camera's `Target Frame` locked to `base_footprint` so the robot
  stays centered regardless of drift — this also fixes a constant
  viewport-rendering offset in RViz's `TopDownOrtho` camera that had pushed
  the subject toward the edge of frame in earlier captures.
- Added a new 3D-perspective cover image (`title_hero_new.png`) showing the
  robot model with the live LiDAR scan cloud.
- Added `src/mini_amr_navigation/rviz/slam.rviz`, a dedicated RViz config for
  the SLAM demo (previously it launched with RViz's blank default).
- Removed superseded screenshots, an old GIF and duplicate map/RViz-config
  copies from `deliverables/` in favor of the video clips above.

---

## v1.0.0

## Project overview

Mini-AMR is a simulated Autonomous Mobile Robot software stack for ROS 2. It
demonstrates a full mobile-robotics pipeline — robot description, teleoperation,
SLAM mapping and Nav2 autonomous navigation — **without Gazebo**. Hardware is
replaced by lightweight nodes that synthesize odometry from `/cmd_vel` and
publish a simulated LiDAR scan, so the entire stack runs on any machine with
ROS 2 and Nav2 installed.

## Main features

- **Robot model** — 4-wheel differential robot with a LiDAR, defined in
  URDF/xacro and visualized in RViz2 with a complete TF tree
  (`map → odom → base_footprint → base_link → {wheels, laser_link}`).
- **Teleoperation** — drive with `teleop_twist_keyboard`; `fake_odom_publisher`
  integrates `/cmd_vel` into odometry and the moving `odom → base_footprint` TF.
- **Simulated LiDAR & perception** — `fake_scan_publisher` (`random` / `clear`
  modes), `scan_analyzer_node` (obstacle alerts) and `safety_zone_marker`
  (RViz safety-zone visualization).
- **SLAM mapping** — `slam_toolbox` builds an occupancy grid from LiDAR, with a
  `nav2_lifecycle_manager` that auto-activates the lifecycle node.
- **Autonomous navigation** — full Nav2 stack (map_server, AMCL, NavFn planner,
  MPPI controller, behaviour tree, lifecycle manager) navigating on a saved map.
- **Portable, parameterized launch files** — package resources resolved via
  `FindPackageShare`; `navigation.launch.py` exposes `map`, `params_file`,
  `use_sim_time` and `use_rviz` arguments.

## Final deliverables (`deliverables/`)

- `Mini_AMR_Final_Report.pdf` / `.docx` — final technical report
- `mini_amr_final_demo.mp4` — 60 s, 1920×1080 demonstration video

> See the [v1.1.0 notes above](#v110--presentation-deck--refreshed-demo-media)
> for the current presentation deck and per-stage demo clips.

### Verified result

Goal `(1.00, 0.80)` reached at `(1.004, 0.836)` — final position error **3.6 cm**;
behaviour-tree result **`SUCCEEDED`** (`controller_server: "Reached the goal!"`,
`bt_navigator: "Goal succeeded"`). Repeat runs consistently succeeded within
tolerance.

## Known limitations

- **Simulated sensors only.** The LiDAR scan is synthetic and not derived from
  the map geometry, so AMCL scan-matching and SLAM do not reflect a real
  environment; the raw SLAM map required denoising for reliable planning.
- **Differential drive in practice.** `mecanum_kinematics_node` is implemented
  but is not wired into any launch file, and the URDF has no mecanum rollers;
  the delivered navigation stack uses a differential-drive motion model.
- **No `/cmd_vel` timeout.** `fake_odom_publisher` keeps integrating the last
  command until a new one arrives, so motion must be explicitly stopped.
- **Standalone perception nodes.** `scan_analyzer_node` and `safety_zone_marker`
  are run manually (`ros2 run`) and are not part of a launch file.
- **No automated CI.** Only the default ament lint tests are present.

## Future improvements

- Replace the synthetic LiDAR with a map-consistent raycast sensor (or Gazebo /
  Ignition) so localization and SLAM operate on real geometry.
- Commit to one kinematic model: either integrate mecanum wheels + rollers with
  an omnidirectional Nav2 motion model, or formally document differential drive.
- Add a `/cmd_vel` watchdog/timeout to `fake_odom_publisher`.
- Integrate the perception/safety nodes into a bringup launch file.
- Add unit/integration tests and a GitHub Actions CI workflow
  (`colcon build` + `colcon test`).

## License

Released under the **Apache License 2.0** — see [`LICENSE`](LICENSE) for details.

---

*This is the initial public release (v1.0.0).*
