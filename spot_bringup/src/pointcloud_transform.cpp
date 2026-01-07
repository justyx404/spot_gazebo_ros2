#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/point_cloud2.hpp"
#include "tf2_ros/buffer.h"
#include "tf2_ros/transform_listener.h"
#include "tf2_sensor_msgs/tf2_sensor_msgs.hpp"
#include "geometry_msgs/msg/transform_stamped.hpp"

class PointCloudTransform : public rclcpp::Node
{
public:
  PointCloudTransform()
  : Node("pointcloud_transform")
  {
    // Declare parameters
    this->declare_parameter("target_frame", "base_link");
    this->declare_parameter("input_topic", "/spot/lidar/points");
    this->declare_parameter("output_topic", "/spot/lidar/points_transformed");

    target_frame_ = this->get_parameter("target_frame").as_string();
    std::string input_topic = this->get_parameter("input_topic").as_string();
    std::string output_topic = this->get_parameter("output_topic").as_string();

    // TF2 setup
    tf_buffer_ = std::make_unique<tf2_ros::Buffer>(this->get_clock());
    tf_listener_ = std::make_shared<tf2_ros::TransformListener>(*tf_buffer_);

    // Subscriber QoS (Best Effort for Gazebo/Sensor input)
    rclcpp::QoS input_qos(10);
    input_qos.reliability(rclcpp::ReliabilityPolicy::BestEffort);
    input_qos.durability(rclcpp::DurabilityPolicy::Volatile);

    // Publisher QoS (Reliable for RViz/Downstream compatibility)
    rclcpp::QoS output_qos(10);
    output_qos.reliability(rclcpp::ReliabilityPolicy::Reliable);
    output_qos.durability(rclcpp::DurabilityPolicy::Volatile);

    // Publisher
    publisher_ = this->create_publisher<sensor_msgs::msg::PointCloud2>(output_topic, output_qos);

    // Subscriber
    subscription_ = this->create_subscription<sensor_msgs::msg::PointCloud2>(
      input_topic,
      input_qos,
      std::bind(&PointCloudTransform::pointcloud_callback, this, std::placeholders::_1));

    RCLCPP_INFO(this->get_logger(), "PointCloud Transform: %s -> %s (target: %s)", 
      input_topic.c_str(), output_topic.c_str(), target_frame_.c_str());
  }

private:
  void pointcloud_callback(const sensor_msgs::msg::PointCloud2::SharedPtr msg)
  {
    std::string source_frame = msg->header.frame_id;
    if (source_frame.empty()) {
       RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 2000, "Received PointCloud2 with empty frame_id");
       return;
    }

    if (source_frame == target_frame_) {
      publisher_->publish(*msg);
      return;
    }

    try {
      // Lookup transform with a short timeout
      geometry_msgs::msg::TransformStamped transform_stamped = 
        tf_buffer_->lookupTransform(target_frame_, source_frame, msg->header.stamp, rclcpp::Duration::from_seconds(0.1));

      sensor_msgs::msg::PointCloud2 cloud_out;
      tf2::doTransform(*msg, cloud_out, transform_stamped);
      publisher_->publish(cloud_out);
    } catch (const tf2::TransformException & ex) {
      RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 2000, "Transform error: %s", ex.what());
    }
  }

  std::string target_frame_;
  std::unique_ptr<tf2_ros::Buffer> tf_buffer_;
  std::shared_ptr<tf2_ros::TransformListener> tf_listener_;
  rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr publisher_;
  rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr subscription_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<PointCloudTransform>());
  rclcpp::shutdown();
  return 0;
}
