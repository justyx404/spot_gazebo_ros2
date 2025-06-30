from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    spot_nav_pkg = FindPackageShare('spot_navigation')

    use_sim_time_arg = DeclareLaunchArgument(
		'use_sim_time',
		default_value='false',  # Set to 'true' for simulation
		description='Use simulation (Gazebo) clock if true'
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

    dlo_yaml_path = PathJoinSubstitution([spot_nav_pkg, 'config', 'dlo.yaml'])
    dlo_odom_node = Node(
    	name = 'dlo_odom',
    	package = 'direct_lidar_odometry',
    	executable = 'dlo_odom_node',
    	output = 'screen',
    	parameters = [
			dlo_yaml_path,
			{'use_sim_time': LaunchConfiguration('use_sim_time')}		
		],
    	remappings = [
    		('imu'		 	, imu_topic_cfg),
    		('pointcloud'	, pointcloud_topic_cfg),
			('filtered_scan', 'dlo/odom_node/filtered_scan'),
    		('odom'         , 'dlo/odom_node/odom'),
    		('pose'			, 'dlo/odom_node/pose'),
    		('kfs' 			, 'dlo/odom_node/odom/keyframe'),
    		('keyframe'		, 'dlo/odom_node/pointcloud/keyframe')
    	]
    )

    dlo_localization_node = Node(
        name = 'dlo_localization',
        package = 'direct_lidar_odometry',
        executable = 'dlo_localization_node',
        output = 'screen',
        parameters = [
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ],
	)

    return LaunchDescription([
        use_sim_time_arg,
    	declare_pointcloud_topic_arg,
    	declare_imu_topic_arg,
    	dlo_odom_node,
        dlo_localization_node
    ])