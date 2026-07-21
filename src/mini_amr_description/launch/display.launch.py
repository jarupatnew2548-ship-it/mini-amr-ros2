from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution, Command


def generate_launch_description():

    robot_description = Command([
        'xacro ',
        PathJoinSubstitution([
            FindPackageShare('mini_amr_description'),
            'urdf',
            'mini_amr.urdf.xacro'
        ])
    ])

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
            parameters=[
                {
                    'robot_description': robot_description
                }
            ],
            output='screen'
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            arguments=[
                 '-d',
                 PathJoinSubstitution([
                   FindPackageShare('mini_amr_description'),
                    'rviz',
                    'mini_amr.rviz'
        ])
    ],
            output='screen'
        )

    ])
