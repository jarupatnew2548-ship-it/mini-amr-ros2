#!/bin/bash
# Launch Nav2 (headless) and record one real navigation run to JSON.
# Usage: bash record_nav.sh GOAL_X GOAL_Y [OUT_JSON]
set +e
GX=${1:-1.0}
GY=${2:-0.0}
OUT=${3:-/tmp/nav_demo.json}

unset DISPLAY WAYLAND_DISPLAY
source /opt/ros/jazzy/setup.bash
source ~/amr_ws/install/setup.bash
cd ~/amr_ws

pkill -f bringup_launch 2>/dev/null; pkill -f component_container 2>/dev/null
pkill -f robot_state_publisher 2>/dev/null; pkill -f fake_ 2>/dev/null
pkill -f nav_demo_recorder 2>/dev/null; pkill -f navigation.launch 2>/dev/null
sleep 2

echo "== launch navigation (headless, use_rviz:=false) =="
nohup ros2 launch mini_amr_navigation navigation.launch.py use_rviz:=false \
  > /tmp/nav.log 2>&1 &
echo "waiting 24s for lifecycle activation..."
sleep 24

echo "== run recorder: goal=($GX,$GY) -> $OUT =="
ros2 run mini_amr_navigation nav_demo_recorder \
  --ros-args -p goal_x:=$GX -p goal_y:=$GY -p out_file:=$OUT 2>&1 | \
  grep -iE "Map received|path received|Goal accepted|Action finished|Recorded"

echo "== nav.log result lines =="
grep -iE "Reached the goal|Goal succeeded|Goal failed|failed to plan" /tmp/nav.log | tail -n 4

echo "== cleanup =="
pkill -f bringup_launch 2>/dev/null; pkill -f component_container 2>/dev/null
pkill -f robot_state_publisher 2>/dev/null; pkill -f fake_ 2>/dev/null
pkill -f nav_demo_recorder 2>/dev/null; pkill -f navigation.launch 2>/dev/null
sleep 2
echo DONE
