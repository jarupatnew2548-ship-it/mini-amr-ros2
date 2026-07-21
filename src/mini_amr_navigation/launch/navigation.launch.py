#!/usr/bin/env python3
"""
Task 11 - Nav2 map-based navigation launch file.

Brings up everything needed to drive the simulated Mini-AMR to a goal on a
previously saved map:

  * robot_state_publisher  -> URDF TF tree (base_footprint -> base_link -> laser_link)
  * fake_odom_publisher    -> integrates /cmd_vel into /odom + TF odom->base_footprint
                              (this is what actually moves the robot toward the goal)
  * fake_scan_publisher    -> /scan (launched in 'clear' mode so AMCL stays stable)
  * nav2_bringup           -> map_server + AMCL (localization) + planner +
                              controller + smoother + behaviors + bt_navigator +
                              lifecycle_manager
  * rviz2                  -> visualisation (map, robot pose, global path, goal)

Usage:
  ros2 launch mini_amr_navigation navigation.launch.py
  ros2 launch mini_amr_navigation navigation.launch.py use_rviz:=false      # headless
  ros2 launch mini_amr_navigation navigation.launch.py map:=/path/to/my_map.yaml
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    Command,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    pkg_nav = FindPackageShare('mini_amr_navigation')
    pkg_desc = FindPackageShare('mini_amr_description')

    # ---------------------------------------------------------------
    # Launch arguments
    # ---------------------------------------------------------------
    map_arg = DeclareLaunchArgument(
        'map',
        default_value=PathJoinSubstitution([pkg_nav, 'maps', 'task11_map.yaml']),
        description='Full path to the saved map YAML file to navigate on '
                    '(task11_map = denoised task10 SLAM map).'
    )
    params_arg = DeclareLaunchArgument(
        'params_file',
        default_value=PathJoinSubstitution([pkg_nav, 'config', 'nav2_params.yaml']),
        description='Full path to the Nav2 parameters file.'
    )
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (/clock) time.'
    )
    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Whether to start RViz2 (set false for headless runs).'
    )

    map_file = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')

    urdf_file = PathJoinSubstitution([pkg_desc, 'urdf', 'mini_amr.urdf.xacro'])
    rviz_config = PathJoinSubstitution([pkg_nav, 'rviz', 'nav2.rviz'])

    # ---------------------------------------------------------------
    # Robot description (URDF): base_footprint -> base_link -> laser_link
    # ---------------------------------------------------------------
    robot_description = ParameterValue(
        Command(['xacro ', urdf_file]),
        value_type=str
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': use_sim_time,
        }]
    )

    # Publishes zero joint states for the (continuous) wheel joints so the
    # wheels get valid TF frames and the RViz RobotModel renders without errors.
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # ---------------------------------------------------------------
    # Fake odometry: subscribes /cmd_vel, publishes /odom and the moving TF
    # odom -> base_footprint (this is what makes the robot drive to the goal).
    # ---------------------------------------------------------------
    fake_odom = Node(
        package='mini_amr_control',
        executable='fake_odom_publisher',
        name='fake_odom_publisher',
        output='screen'
    )

    # ---------------------------------------------------------------
    # Fake LiDAR in 'clear' (open-space) mode so AMCL localisation holds the
    # initial pose steadily instead of chasing a random scan.
    # ---------------------------------------------------------------
    fake_scan = Node(
        package='mini_amr_sensors',
        executable='fake_scan_publisher',
        name='fake_scan_publisher',
        output='screen',
        parameters=[{'pattern': 'clear'}]
    )

    # ---------------------------------------------------------------
    # Nav2 bringup = map_server + AMCL (localization) + planner + controller +
    # smoother + behaviors + bt_navigator + lifecycle manager.
    # ---------------------------------------------------------------
    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('nav2_bringup'),
                'launch',
                'bringup_launch.py'
            ])
        ),
        launch_arguments={
            'map': map_file,
            'params_file': params_file,
            'use_sim_time': use_sim_time,
        }.items()
    )

    # ---------------------------------------------------------------
    # RViz2
    # ---------------------------------------------------------------
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        output='screen',
        condition=IfCondition(use_rviz)
    )

    return LaunchDescription([
        map_arg,
        params_arg,
        use_sim_time_arg,
        use_rviz_arg,
        robot_state_publisher,
        joint_state_publisher,
        fake_odom,
        fake_scan,
        nav2_bringup,
        rviz,
    ])
