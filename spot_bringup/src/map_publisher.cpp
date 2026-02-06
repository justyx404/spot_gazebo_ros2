#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <pcl_conversions/pcl_conversions.h>
#include <pcl/io/pcd_io.h>
#include <pcl/point_types.h>
#include <pcl/filters/voxel_grid.h>
#include <pcl/sample_consensus/method_types.h>
#include <pcl/sample_consensus/model_types.h>
#include <pcl/segmentation/sac_segmentation.h>
#include <tf2_ros/static_transform_broadcaster.h>
#include <geometry_msgs/msg/transform_stamped.hpp>

class MapPublisher : public rclcpp::Node
{
public:
  MapPublisher() : Node("map_publisher")
  {
    // Parameters
    this->declare_parameter<std::string>("map_path", "");
    this->declare_parameter<std::string>("frame_id", "map");
    this->declare_parameter<double>("publish_rate", 5.0);
    this->declare_parameter<double>("leaf_size", 0.25);
    this->declare_parameter<double>("ransac_threshold", 0.15);

    std::string map_path;
    this->get_parameter("map_path", map_path);
    this->get_parameter("frame_id", frame_id_);
    double publish_rate;
    this->get_parameter("publish_rate", publish_rate);
    double leaf_size;
    this->get_parameter("leaf_size", leaf_size);
    double ransac_threshold;
    this->get_parameter("ransac_threshold", ransac_threshold);

    if (map_path.empty()) {
      RCLCPP_ERROR(this->get_logger(), "Parameter 'map_path' is empty. Exiting.");
      return; 
    }

    // Load PCD
    pcl::PointCloud<pcl::PointXYZI>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZI>);
    if (pcl::io::loadPCDFile<pcl::PointXYZI>(map_path, *cloud) == -1) {
      RCLCPP_ERROR(this->get_logger(), "Couldn't read file: %s", map_path.c_str());
      return;
    }
    RCLCPP_INFO(this->get_logger(), "Raw map loaded with %lu points", cloud->points.size());

    // Filter
    if (leaf_size > 0.0) {
      RCLCPP_INFO(this->get_logger(), "Filtering global map with leaf size: %f ...", leaf_size);
      pcl::PointCloud<pcl::PointXYZI>::Ptr filtered_cloud(new pcl::PointCloud<pcl::PointXYZI>);
      pcl::VoxelGrid<pcl::PointXYZI> voxel_grid;
      voxel_grid.setLeafSize(leaf_size, leaf_size, leaf_size);
      voxel_grid.setInputCloud(cloud);
      voxel_grid.filter(*filtered_cloud);
      cloud = filtered_cloud;
      RCLCPP_INFO(this->get_logger(), "Filtered map to %lu points", cloud->points.size());
    } else {
      RCLCPP_INFO(this->get_logger(), "No filtering applied to map.");
    }

    // Pre-process intensities using RANSAC ground segmentation
    RCLCPP_INFO(this->get_logger(), "Pre-processing global map for ground segmentation (thresh: %f)...", ransac_threshold);
    pcl::ModelCoefficients::Ptr coefficients(new pcl::ModelCoefficients);
    pcl::PointIndices::Ptr inliers(new pcl::PointIndices);
    pcl::SACSegmentation<pcl::PointXYZI> seg;

    seg.setOptimizeCoefficients(true);
    seg.setModelType(pcl::SACMODEL_PLANE);
    seg.setMethodType(pcl::SAC_RANSAC);
    seg.setDistanceThreshold(ransac_threshold);
    seg.setInputCloud(cloud);
    seg.segment(*inliers, *coefficients);

    if (inliers->indices.empty())
    {
      RCLCPP_WARN(this->get_logger(), "Could not estimate a planar model. All points marked as non-ground.");
      for (size_t i = 0; i < cloud->points.size(); ++i) {
        cloud->points[i].intensity = 1.0; // Non-Ground
      }
    }
    else
    {
      // Assume all points are non-ground initially
      for (size_t i = 0; i < cloud->points.size(); ++i) {
        cloud->points[i].intensity = 1.0; // Non-Ground
      }

      // Mark RANSAC inliers as ground
      for (size_t i = 0; i < inliers->indices.size(); ++i) {
        cloud->points[inliers->indices[i]].intensity = 0.0; // Ground
      }
      RCLCPP_INFO(this->get_logger(), "Segmented ground plane with %lu points.", inliers->indices.size());
    }

    // Convert to ROS message
    pcl::toROSMsg(*cloud, cloud_msg_);
    cloud_msg_.header.frame_id = frame_id_;

    // Publisher
    publisher_ = this->create_publisher<sensor_msgs::msg::PointCloud2>("global_cloud", rclcpp::QoS(rclcpp::KeepLast(1)).transient_local().reliable());

    // Timer
    timer_ = this->create_wall_timer(
      std::chrono::duration<double>(1.0 / publish_rate),
      std::bind(&MapPublisher::publish_map, this));

    // Static Transform Broadcaster (map -> odom_lidar identity)
    static_broadcaster_ = std::make_shared<tf2_ros::StaticTransformBroadcaster>(this);
    publish_static_transform();
  }

private:
  void publish_map()
  {
    cloud_msg_.header.stamp = this->now();
    publisher_->publish(cloud_msg_);
  }

  void publish_static_transform()
  {
    geometry_msgs::msg::TransformStamped t;
    t.header.stamp = this->now();
    t.header.frame_id = "map";
    t.child_frame_id = "odom_lidar";

    t.transform.translation.x = 0.0;
    t.transform.translation.y = 0.0;
    t.transform.translation.z = 0.0;
    t.transform.rotation.x = 0.0;
    t.transform.rotation.y = 0.0;
    t.transform.rotation.z = 0.0;
    t.transform.rotation.w = 1.0;

    static_broadcaster_->sendTransform(t);
  }

  std::string frame_id_;
  sensor_msgs::msg::PointCloud2 cloud_msg_;
  rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
  std::shared_ptr<tf2_ros::StaticTransformBroadcaster> static_broadcaster_;
};

int main(int argc, char **argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<MapPublisher>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}