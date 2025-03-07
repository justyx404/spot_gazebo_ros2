import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class ThermalToRGB(Node):
    def __init__(self):
        super().__init__('thermal_to_rgb')
        self.bridge = CvBridge()
        self.sub = self.create_subscription(Image, '/spot/thermal_camera', self.image_callback, 10)
        self.pub = self.create_publisher(Image, '/spot/thermal_rgb', 10)
        self.colormap = cv2.COLORMAP_INFERNO

    def image_callback(self, msg):
        cv_16bit = self.bridge.imgmsg_to_cv2(msg, desired_encoding='mono16')
        cv_8bit = cv2.normalize(cv_16bit, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        cv_rgb = cv2.applyColorMap(cv_8bit, self.colormap)
            
        # Convert back to ROS Image
        ros_rgb = self.bridge.cv2_to_imgmsg(cv_rgb, encoding='bgr8')
        ros_rgb.header = msg.header  # Preserve timestamp/frame_id
            
        self.pub.publish(ros_rgb)

def main(args=None):
    rclpy.init(args=args)
    node = ThermalToRGB()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()