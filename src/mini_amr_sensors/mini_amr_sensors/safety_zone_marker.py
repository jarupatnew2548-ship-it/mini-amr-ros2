import rclpy
from rclpy.node import Node

from sensor_msgs.msg import LaserScan
from visualization_msgs.msg import Marker, MarkerArray


class SafetyZoneVisualizer(Node):

    def __init__(self):
        super().__init__('safety_zone_visualizer')

        self.marker_pub = self.create_publisher(
            MarkerArray,
            '/safety_markers',
            10
        )

        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.get_logger().info("Safety Zone Node Started")

    def create_zone_marker(self, x, y, z, r, g, b, marker_id):
        marker = Marker()
        marker.header.frame_id = "odom"
        marker.header.stamp = self.get_clock().now().to_msg()

        marker.ns = "safety_zone"
        marker.id = marker_id
        marker.type = Marker.CUBE
        marker.action = Marker.ADD

        marker.pose.position.x = x
        marker.pose.position.y = y
        marker.pose.position.z = z

        marker.scale.x = 0.8
        marker.scale.y = 0.8
        marker.scale.z = 0.3

        marker.color.r = r
        marker.color.g = g
        marker.color.b = b
        marker.color.a = 0.8

        return marker

    def create_text_marker(self, text):
        marker = Marker()
        marker.header.frame_id = "odom"
        marker.header.stamp = self.get_clock().now().to_msg()

        marker.ns = "warning"
        marker.id = 99
        marker.type = Marker.TEXT_VIEW_FACING
        marker.action = Marker.ADD

        marker.pose.position.x = 0.0
        marker.pose.position.y = 0.0
        marker.pose.position.z = 1.0

        marker.scale.z = 0.4
        marker.color.r = 1.0
        marker.color.g = 0.0
        marker.color.b = 0.0
        marker.color.a = 1.0

        marker.text = text
        return marker

    def scan_callback(self, msg):

        self.get_logger().info("Scan callback triggered")

        marker_array = MarkerArray()

        min_distance = min(msg.ranges)

        self.get_logger().info(f"Minimum distance: {min_distance}")

        danger = min_distance < 0.8

        if danger:
            color = (1.0, 0.0, 0.0)  # RED
            text = "⚠ DANGER OBSTACLE!"
        else:
            color = (0.0, 0.0, 1.0)  # BLUE
            text = "SAFE"

        r, g, b = color

        # Front zone
        marker_array.markers.append(
            self.create_zone_marker(0.8, 0.0, 0.0, r, g, b, 0)
        )

        # Left zone
        marker_array.markers.append(
            self.create_zone_marker(0.5, 0.5, 0.0, r, g, b, 1)
        )

        # Right zone
        marker_array.markers.append(
            self.create_zone_marker(0.5, -0.5, 0.0, r, g, b, 2)
        )

        # Text warning
        marker_array.markers.append(
            self.create_text_marker(text)
        )

        self.marker_pub.publish(marker_array)


def main(args=None):
    rclpy.init(args=args)
    node = SafetyZoneVisualizer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()