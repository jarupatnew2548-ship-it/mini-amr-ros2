from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import PathJoinSubstitution, Command


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

        # Robot model
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': False
            }]
        ),

        # Fake odometry
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

        # NOTE: mini_amr_control/tf_broadcaster is intentionally NOT launched.
        # It publishes a *fixed* odom -> base_link transform, which conflicts
        # with fake_odom_publisher's moving odom -> base_footprint (base_link
        # already hangs off base_footprint via the URDF).  Running both pins the
        # robot at the origin in RViz even though odometry is moving.

    ])
