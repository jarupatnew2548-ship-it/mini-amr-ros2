import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool


class ScanAnalyzerNode(Node):

    def __init__(self):
        super().__init__('scan_analyzer_node')

        # subscriber
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.callback,
            10
        )

        # Publisher for obstacle warning information
        self.alert_pub = self.create_publisher(Bool, '/obstacle_alert', 10)

        self.safety_threshold = 0.5
        self.get_logger().info("Scan Analyzer Node Started")

    def callback(self, msg):

        ranges = msg.ranges
        total = len(ranges)

        front = ranges[int(0.95 * total):] + ranges[:int(0.05 * total)]
        left  = ranges[int(0.25 * total):int(0.45 * total)]
        right = ranges[int(0.55 * total):int(0.75 * total)]

        front = [r for r in front if r > 0.0]
        left  = [r for r in left if r > 0.0]
        right = [r for r in right if r > 0.0]

        if not front:
            return

        min_front = min(front)
        min_left = min(left) if left else 999
        min_right = min(right) if right else 999

        self.get_logger().info(
            f"Front: {min_front:.2f} | Left: {min_left:.2f} | Right: {min_right:.2f}"
        )

        # alert logic
        alert = Bool()
        alert.data = min_front < self.safety_threshold

        self.alert_pub.publish(alert)

        if alert.data:
            self.get_logger().warn("⚠ OBSTACLE DETECTED FRONT!")


def main(args=None):
    rclpy.init(args=args)
    node = ScanAnalyzerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()