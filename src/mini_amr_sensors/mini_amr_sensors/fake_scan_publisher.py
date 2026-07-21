import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from builtin_interfaces.msg import Time
from rclpy.time import Time
import math
import random

class FakeScanPublisher(Node):

    def __init__(self):
        super().__init__('fake_scan_publisher')

        self.pub = self.create_publisher(LaserScan, '/scan', 10)
        self.timer = self.create_timer(0.2, self.publish_scan)

        self.ranges_num = 360

        # 'random' (default) keeps the original noisy-obstacle behaviour used by
        # the earlier tasks.  'clear' publishes an open-space scan (no returns)
        # so that AMCL localisation stays stable during map-based navigation.
        self.pattern = self.declare_parameter(
            'pattern', 'random'
        ).get_parameter_value().string_value

        self.get_logger().info(
            f"Fake Scan Publisher Started (pattern='{self.pattern}')"
        )

    def publish_scan(self):

        msg = LaserScan()

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "laser_link"
        msg.angle_min = 0.0
        msg.angle_max = 2 * math.pi
        msg.angle_increment = (2 * math.pi) / self.ranges_num
        msg.range_min = 0.1
        msg.range_max = 3.0

        ranges = []

        if self.pattern == 'clear':
            # Open space: report "no return" everywhere so AMCL does not try to
            # correct against a non-existent obstacle and map->odom stays steady.
            ranges = [float('inf')] * self.ranges_num
        else:
            for i in range(self.ranges_num):

                if 170 < i < 190:
                    ranges.append(random.uniform(0.2, 0.5))  # obstacle front
                else:
                    ranges.append(random.uniform(0.8, 2.5))

        msg.ranges = ranges
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = FakeScanPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
