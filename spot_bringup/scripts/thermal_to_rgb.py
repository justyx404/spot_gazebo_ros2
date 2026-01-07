#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class ThermalToRGB(Node):
    def __init__(self):
        super().__init__('thermal_to_rgb')
        self.bridge = CvBridge()

        # Best Effort QoS for subscriber (to match Gazebo)
        input_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # Reliable QoS for publisher (for RViz)
        output_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.sub = self.create_subscription(Image, '/spot/camera/thermal_camera', self.image_callback, input_qos)
        self.pub = self.create_publisher(Image, '/spot/camera/thermal_rgb', output_qos)
        self.colormap = cv2.COLORMAP_INFERNO
        self.get_logger().info("ThermalToRGB node started.")

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='mono16')
            # Normalize 16-bit to 8-bit
            cv_8bit = cv2.normalize(cv_image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

            # Apply colormap
            cv_rgb = cv2.applyColorMap(cv_8bit, self.colormap)

            # Convert back to ROS Image
            ros_rgb = self.bridge.cv2_to_imgmsg(cv_rgb, encoding='bgr8')
            ros_rgb.header = msg.header  # Preserve timestamp/frame_id

            self.pub.publish(ros_rgb)

        except Exception as e:
            self.get_logger().error(f"Error processing thermal image: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = ThermalToRGB()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
