#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped, Twist

from tf2_ros import TransformBroadcaster

from tf_transformations import quaternion_from_euler


class FakeOdomPublisher(Node):

    def __init__(self):
        super().__init__('fake_odom_publisher')

        # Publish odometry
        self.odom_pub = self.create_publisher(
            Odometry,
            '/odom',
            10
        )

        # Subscribe to cmd_vel
        self.cmd_sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_callback,
            10
        )

        # Publish TF
        self.tf_broadcaster = TransformBroadcaster(self)

        # Robot position
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

        # Robot velocity from /cmd_vel
        self.vx = 0.0
        self.vy = 0.0
        self.wz = 0.0

        # Timer period
        self.dt = 0.1

        self.timer = self.create_timer(
            self.dt,
            self.publish_odom
        )

        self.get_logger().info(
            'Cmd_vel Odom Publisher Started'
        )


    # Receive velocity command
    def cmd_callback(self, msg):

        self.vx = msg.linear.x
        self.vy = msg.linear.y
        self.wz = msg.angular.z



    # Calculate and publish odometry
    def publish_odom(self):

        # Update robot orientation
        self.theta += self.wz * self.dt


        # Convert robot velocity frame to odom frame
        self.x += (
            self.vx * math.cos(self.theta)
            - self.vy * math.sin(self.theta)
        ) * self.dt


        self.y += (
            self.vx * math.sin(self.theta)
            + self.vy * math.cos(self.theta)
        ) * self.dt


        now = self.get_clock().now().to_msg()


        # Convert yaw to quaternion
        q = quaternion_from_euler(
            0,
            0,
            self.theta
        )


        # -------- Odometry message --------

        odom = Odometry()

        odom.header.stamp = now
        odom.header.frame_id = "odom"

        odom.child_frame_id = "base_footprint"


        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = 0.0


        odom.pose.pose.orientation.x = q[0]
        odom.pose.pose.orientation.y = q[1]
        odom.pose.pose.orientation.z = q[2]
        odom.pose.pose.orientation.w = q[3]


        # Velocity information

        odom.twist.twist.linear.x = self.vx
        odom.twist.twist.linear.y = self.vy
        odom.twist.twist.angular.z = self.wz


        self.odom_pub.publish(odom)



        # -------- TF odom -> base_footprint --------

        tf = TransformStamped()

        tf.header.stamp = now

        tf.header.frame_id = "odom"

        tf.child_frame_id = "base_footprint"


        tf.transform.translation.x = self.x
        tf.transform.translation.y = self.y
        tf.transform.translation.z = 0.0


        tf.transform.rotation.x = q[0]
        tf.transform.rotation.y = q[1]
        tf.transform.rotation.z = q[2]
        tf.transform.rotation.w = q[3]


        self.tf_broadcaster.sendTransform(tf)



def main(args=None):

    rclpy.init(args=args)

    node = FakeOdomPublisher()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()



if __name__ == '__main__':
    main()