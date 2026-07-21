#!/usr/bin/env python3
"""
nav_demo_recorder
=================

Drives one complete Nav2 map-based navigation run and records everything needed
to visualise it (map, planned global path, executed trajectory, goal, result):

  1. waits for the map and the Nav2 lifecycle to be up,
  2. publishes the AMCL initial pose,
  3. sends a NavigateToPose goal,
  4. records the first planned path published on /plan,
  5. samples the executed trajectory from TF (map -> base_footprint),
  6. waits for the action result and writes a JSON summary.

Parameters (ROS):
  goal_x, goal_y, goal_yaw   : goal pose in the map frame (default 1.0, 0.0, 0.0)
  init_x, init_y, init_yaw   : initial pose in the map frame (default 0.0)
  out_file                   : JSON output path (default /tmp/nav_demo.json)
"""

import json
import math

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import (
    QoSProfile,
    QoSDurabilityPolicy,
    QoSReliabilityPolicy,
    QoSHistoryPolicy,
)

import tf2_ros
from geometry_msgs.msg import PoseWithCovarianceStamped
from nav_msgs.msg import OccupancyGrid, Path
from nav2_msgs.action import NavigateToPose
from tf_transformations import quaternion_from_euler, euler_from_quaternion


class NavDemoRecorder(Node):

    def __init__(self):
        super().__init__('nav_demo_recorder')

        self.declare_parameter('goal_x', 1.0)
        self.declare_parameter('goal_y', 0.0)
        self.declare_parameter('goal_yaw', 0.0)
        self.declare_parameter('init_x', 0.0)
        self.declare_parameter('init_y', 0.0)
        self.declare_parameter('init_yaw', 0.0)
        self.declare_parameter('out_file', '/tmp/nav_demo.json')

        gp = self.get_parameter
        self.goal = (gp('goal_x').value, gp('goal_y').value, gp('goal_yaw').value)
        self.init = (gp('init_x').value, gp('init_y').value, gp('init_yaw').value)
        self.out_file = gp('out_file').value

        # Map arrives with transient-local durability from map_server.
        map_qos = QoSProfile(
            depth=1,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
            reliability=QoSReliabilityPolicy.RELIABLE,
            history=QoSHistoryPolicy.KEEP_LAST,
        )
        self.map_msg = None
        self.create_subscription(OccupancyGrid, '/map', self._on_map, map_qos)

        self.plan_msg = None
        self.create_subscription(Path, '/plan', self._on_plan, 10)

        self.init_pub = self.create_publisher(
            PoseWithCovarianceStamped, '/initialpose', 10)

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        self.nav_client = ActionClient(self, NavigateToPose, '/navigate_to_pose')

        self.trajectory = []          # map-frame:  (t, x, y, yaw)
        self.odom_trajectory = []     # odom-frame (ground truth): (t, x, y, yaw)
        self.result_status = None
        self.result_code = None
        self.t0 = None

    # ---------------- callbacks ----------------
    def _on_map(self, msg):
        if self.map_msg is None:
            self.get_logger().info(
                f'Map received: {msg.info.width}x{msg.info.height} '
                f'@ {msg.info.resolution} m/cell')
        self.map_msg = msg

    def _on_plan(self, msg):
        if not self.plan_msg and msg.poses:
            self.plan_msg = msg
            self.get_logger().info(f'Planned path received: {len(msg.poses)} poses')

    # ---------------- helpers ----------------
    def _now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def _lookup(self, parent, child):
        try:
            tf = self.tf_buffer.lookup_transform(parent, child, rclpy.time.Time())
        except Exception:
            return None
        t = tf.transform.translation
        q = tf.transform.rotation
        yaw = euler_from_quaternion([q.x, q.y, q.z, q.w])[2]
        return (t.x, t.y, yaw)

    def sample_pose(self):
        m = self._lookup('map', 'base_footprint')
        o = self._lookup('odom', 'base_footprint')
        if m is None:
            return None
        if self.t0 is None:
            self.t0 = self._now()
        ts = self._now() - self.t0
        self.trajectory.append((ts, m[0], m[1], m[2]))
        if o is not None:
            self.odom_trajectory.append((ts, o[0], o[1], o[2]))
        return m

    def publish_initial_pose(self):
        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = 'map'
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.pose.pose.position.x = float(self.init[0])
        msg.pose.pose.position.y = float(self.init[1])
        q = quaternion_from_euler(0.0, 0.0, float(self.init[2]))
        msg.pose.pose.orientation.x = q[0]
        msg.pose.pose.orientation.y = q[1]
        msg.pose.pose.orientation.z = q[2]
        msg.pose.pose.orientation.w = q[3]
        # modest covariance so AMCL trusts the seed
        msg.pose.covariance[0] = 0.25
        msg.pose.covariance[7] = 0.25
        msg.pose.covariance[35] = 0.068
        for _ in range(5):
            msg.header.stamp = self.get_clock().now().to_msg()
            self.init_pub.publish(msg)
            self._spin(0.2)

    def build_goal(self):
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = float(self.goal[0])
        goal.pose.pose.position.y = float(self.goal[1])
        q = quaternion_from_euler(0.0, 0.0, float(self.goal[2]))
        goal.pose.pose.orientation.x = q[0]
        goal.pose.pose.orientation.y = q[1]
        goal.pose.pose.orientation.z = q[2]
        goal.pose.pose.orientation.w = q[3]
        return goal

    def _spin(self, seconds):
        end = self._now() + seconds
        while self._now() < end and rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.05)

    # ---------------- main sequence ----------------
    def run(self):
        self.get_logger().info('Waiting for /map ...')
        while self.map_msg is None and rclpy.ok():
            self._spin(0.2)

        self.get_logger().info('Waiting for /navigate_to_pose action server ...')
        while not self.nav_client.wait_for_server(timeout_sec=1.0) and rclpy.ok():
            pass

        self.get_logger().info('Publishing initial pose ...')
        self.publish_initial_pose()
        self._spin(2.0)  # let AMCL settle map->odom

        self.get_logger().info(f'Sending goal {self.goal} ...')
        send_future = self.nav_client.send_goal_async(self.build_goal())
        while not send_future.done() and rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.05)
        gh = send_future.result()
        if not gh.accepted:
            self.get_logger().error('Goal rejected!')
            return
        self.get_logger().info('Goal accepted.')

        result_future = gh.get_result_async()
        # sample trajectory until the action completes
        while rclpy.ok() and not result_future.done():
            self.sample_pose()
            self._spin(0.1)

        res = result_future.result()
        self.result_status = int(res.status)  # 4 == SUCCEEDED
        self.sample_pose()
        self.get_logger().info(f'Action finished, status={self.result_status}')

        self.dump()

    # ---------------- output ----------------
    def dump(self):
        m = self.map_msg
        data = {
            'map': {
                'width': m.info.width,
                'height': m.info.height,
                'resolution': m.info.resolution,
                'origin': [m.info.origin.position.x,
                           m.info.origin.position.y],
                'data': list(m.data),
            },
            'init_pose': self.init,
            'goal_pose': self.goal,
            'plan': [
                [p.pose.position.x, p.pose.position.y]
                for p in (self.plan_msg.poses if self.plan_msg else [])
            ],
            'trajectory': [list(p) for p in self.trajectory],
            'odom_trajectory': [list(p) for p in self.odom_trajectory],
            'result_status': self.result_status,
            'succeeded': self.result_status == 4,
        }
        with open(self.out_file, 'w') as f:
            json.dump(data, f)

        # console summary
        end = self.trajectory[-1] if self.trajectory else (0, 0, 0, 0)
        dist = math.hypot(end[1] - self.goal[0], end[2] - self.goal[1])
        self.get_logger().info(
            f'Recorded: plan={len(data["plan"])} poses, '
            f'trajectory={len(data["trajectory"])} samples, '
            f'final=({end[1]:.2f},{end[2]:.2f}), goal_err={dist:.3f} m, '
            f'succeeded={data["succeeded"]} -> {self.out_file}')


def main(args=None):
    rclpy.init(args=args)
    node = NavDemoRecorder()
    try:
        node.run()
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
