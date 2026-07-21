#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from std_msgs.msg import Float32


class MecanumKinematicsNode(Node):

    def __init__(self):
        super().__init__('mecanum_kinematics_node')

        # Subscribe velocity command
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )

        # Wheel speed publishers
        self.fl_pub = self.create_publisher(
            Float32,
            '/wheel/front_left_speed',
            10
        )

        self.fr_pub = self.create_publisher(
            Float32,
            '/wheel/front_right_speed',
            10
        )

        self.rl_pub = self.create_publisher(
            Float32,
            '/wheel/rear_left_speed',
            10
        )

        self.rr_pub = self.create_publisher(
            Float32,
            '/wheel/rear_right_speed',
            10
        )

        # Robot parameters
        self.wheel_radius = 0.05
        self.length = 0.3
        self.width = 0.3

        self.get_logger().info(
            "Mecanum Kinematics Node Started"
        )


    def cmd_vel_callback(self, msg):

        vx = msg.linear.x
        vy = msg.linear.y
        wz = msg.angular.z

        r = self.wheel_radius
        L = self.length
        W = self.width


        # Inverse kinematics equation
        front_left = (vx - vy - (L+W)*wz) / r
        front_right = (vx + vy + (L+W)*wz) / r
        rear_left = (vx + vy - (L+W)*wz) / r
        rear_right = (vx - vy + (L+W)*wz) / r


        self.publish_speed(self.fl_pub, front_left)
        self.publish_speed(self.fr_pub, front_right)
        self.publish_speed(self.rl_pub, rear_left)
        self.publish_speed(self.rr_pub, rear_right)


        self.get_logger().info(
            f"FL:{front_left:.2f} "
            f"FR:{front_right:.2f} "
            f"RL:{rear_left:.2f} "
            f"RR:{rear_right:.2f}"
        )


    def publish_speed(self, publisher, speed):

        msg = Float32()
        msg.data = speed
        publisher.publish(msg)



def main(args=None):

    rclpy.init(args=args)

    node = MecanumKinematicsNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
