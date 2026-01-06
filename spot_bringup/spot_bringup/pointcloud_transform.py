#!/usr/bin/env python3
"""
Minimal node to transform PointCloud2 messages from one frame to another using TF2.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from rclpy.time import Time
from rclpy.duration import Duration
from sensor_msgs.msg import PointCloud2
import tf2_ros
from tf2_sensor_msgs.tf2_sensor_msgs import do_transform_cloud


class PointCloudTransform(Node):
    def __init__(self):
        super().__init__('pointcloud_transform')

        # Declare parameters
        self.declare_parameter('target_frame', 'base_link')
        self.declare_parameter('input_topic', '/spot/lidar/points')
        self.declare_parameter('output_topic', '/spot/lidar/points_transformed')

        self.target_frame = self.get_parameter('target_frame').get_parameter_value().string_value
        input_topic = self.get_parameter('input_topic').get_parameter_value().string_value
        output_topic = self.get_parameter('output_topic').get_parameter_value().string_value

        # TF2 setup
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # QoS profile for sensor data
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # Publisher and subscriber
        self.publisher = self.create_publisher(PointCloud2, output_topic, qos)
        self.subscription = self.create_subscription(
            PointCloud2,
            input_topic,
            self.pointcloud_callback,
            qos
        )

        self.get_logger().info(
            f'PointCloud Transform: {input_topic} -> {output_topic} (target: {self.target_frame})'
        )

    def pointcloud_callback(self, msg: PointCloud2):
        source_frame = msg.header.frame_id

        # Skip if already in target frame
        if source_frame == self.target_frame:
            self.publisher.publish(msg)
            return

        try:
            # Lookup the transform at the message timestamp
            transform_stamped = self.tf_buffer.lookup_transform(
                self.target_frame,
                source_frame,
                Time.from_msg(msg.header.stamp),
                timeout=Duration(seconds=1.0)
            )

            # Apply the transform to the point cloud
            cloud_out = do_transform_cloud(msg, transform_stamped)

            # Publish the transformed point cloud
            self.publisher.publish(cloud_out)

        except (tf2_ros.LookupException, tf2_ros.ConnectivityException,
                tf2_ros.ExtrapolationException) as ex:
            self.get_logger().warn(
                f'Transform error: {ex}',
                throttle_duration_sec=2.0
            )


def main(args=None):
    rclpy.init(args=args)
    node = PointCloudTransform()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
