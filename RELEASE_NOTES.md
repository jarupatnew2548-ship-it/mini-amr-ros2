# Release Notes — Mini-AMR ROS 2 v1.0.0

**Platform:** ROS 2 Jazzy Jalisco · Ubuntu 24.04.4 LTS (WSL2) · Python 3.12

---

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
- `mini_amr_final_demo.mp4` — 60 s, 1280×720 demonstration video
- `NAVIGATION_NOTES.md` — navigation architecture and results write-up
- `navigation.gif`, `rviz_map_path.png`, `rviz_map_pose.png`,
  `rviz_fullwindow.png`, `map_path_plot.png` — RViz captures and plots
- `final_map.pgm` / `final_map.yaml` — saved occupancy map
- `mini_amr_navigation.rviz` — navigation RViz configuration

### Verified result

Goal `(1.0, 0.8)` reached at `(1.04, 0.79)` — final position error **4.2 cm**;
behaviour-tree result **`SUCCEEDED`** (`controller_server: "Reached the goal!"`,
`bt_navigator: "Goal succeeded"`). Repeat runs: 5.5 cm and 9.6 cm error, 3/3
successful.

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
