from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    robot_description = ParameterValue(
        Command([
            'xacro ',
            PathJoinSubstitution([
                FindPackageShare('mini_amr_description'),
                'urdf',
                'mini_amr.urdf.xacro'
            ])
        ]),
        value_type=str
    )

    return LaunchDescription([

        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            output='screen'
        ),
        
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[
                {
                    'robot_description': robot_description
                }
            ],
            output='screen'
        ),

        # Fake Odometry
        Node(
            package='mini_amr_control',
            executable='fake_odom_publisher',
            name='fake_odom_publisher',
            output='screen'
        ),

        # Fake LiDAR
        Node(
            package='mini_amr_sensors',
            executable='fake_scan_publisher',
            name='fake_scan_publisher',
            output='screen'
        ),

        # NOTE: mini_amr_sensors/tf_broadcaster is intentionally NOT launched.
        # It publishes a *fixed* odom -> base_link transform that conflicts with
        # fake_odom_publisher's moving odom -> base_footprint, pinning the robot
        # at the origin so SLAM could never map while driving.

        # SLAM Toolbox
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[
                {
                    'use_sim_time': False,
                    'odom_frame': 'odom',
                    'map_frame': 'map',
                    'base_frame': 'base_link',
                    'scan_topic': '/scan'
                }
            ]
        ),

        # slam_toolbox is a LIFECYCLE node in ROS 2 Jazzy: on start-up it stays
        # 'unconfigured' (no /scan subscription, no /map publisher, no map->odom
        # TF) until something transitions it.  This lifecycle manager configures
        # and activates it automatically so mapping actually starts.
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_slam',
            output='screen',
            parameters=[{
                'autostart': True,
                'node_names': ['slam_toolbox'],
            }]
        ),

        # RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen'
        )

    ])