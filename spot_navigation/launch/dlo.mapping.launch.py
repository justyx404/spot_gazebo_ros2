from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    current_pkg = FindPackageShare('direct_lidar_odometry')
    spot_nav_pkg = FindPackageShare('spot_navigation')

    rviz_cfg = LaunchConfiguration('rviz', default='false')
    declare_rviz_arg = DeclareLaunchArgument(
    	'rviz',
    	default_value = rviz_cfg,
    	description = 'Whether or not to launch RViz'
    )

    pointcloud_topic_cfg = LaunchConfiguration('pointcloud_topic', default='/spot/lidar/points')
    declare_pointcloud_topic_arg = DeclareLaunchArgument(
    	'pointcloud_topic',
    	default_value = pointcloud_topic_cfg,
    	description = 'Input point cloud topic name'
    )

    imu_topic_cfg = LaunchConfiguration('imu_topic', default = 'dlo_imu_raw')
    declare_imu_topic_arg = DeclareLaunchArgument(
    	'imu_topic',
    	default_value = imu_topic_cfg,
    	description = 'Input IMU topic name'
    )

    dlo_yaml_path = PathJoinSubstitution([current_pkg, 'cfg', 'dlo.yaml'])
    dlo_params_yaml_path = PathJoinSubstitution([current_pkg, 'cfg', 'params.yaml'])

    dlo_odom_node = Node(
    	name = 'dlo_odom',
    	package = 'direct_lidar_odometry',
    	executable = 'dlo_odom_node',
    	output = 'screen',
    	parameters = [dlo_yaml_path, dlo_params_yaml_path],
    	remappings = [
    		('pointcloud', pointcloud_topic_cfg),
    		('imu', imu_topic_cfg),
    		('odom', 'dlo/odom_node/odom'),
    		('pose', 'dlo/odom_node/pose'),
    		('kfs', 'dlo/odom_node/odom/keyframe'),
    		('keyframe', 'dlo/odom_node/pointcloud/keyframe')
    	]
    )

    dlo_map_node = Node(
    	name = 'dlo_map',
    	package = 'direct_lidar_odometry',
    	executable = 'dlo_map_node',
    	output = 'screen',
    	parameters = [dlo_yaml_path, dlo_params_yaml_path],
    	remappings = [
    		('keyframes', 'dlo/odom_node/pointcloud/keyframe'),
    		('map', 'dlo/map_node/map'),
            ('save_pcd', 'dlo_map/save_pcd')
    	]
    )

    rviz_config_path = PathJoinSubstitution([spot_nav_pkg, 'config', 'dlo.rviz'])
    rviz_node = Node(
    	name = 'dlo_rviz',
    	package = 'rviz2',
    	executable = 'rviz2',
    	arguments = ['-d', rviz_config_path],
    	output = 'screen',
    	condition = IfCondition(LaunchConfiguration('rviz'))
    )

    return LaunchDescription([
    	declare_rviz_arg,
    	declare_pointcloud_topic_arg,
    	declare_imu_topic_arg,
    	dlo_odom_node,
    	dlo_map_node,
    	rviz_node
    ])