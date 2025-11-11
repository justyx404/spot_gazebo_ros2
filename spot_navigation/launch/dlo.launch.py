from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler, Shutdown
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.event_handlers import OnProcessExit


def generate_launch_description():
    spot_nav_pkg = FindPackageShare('spot_navigation')

    rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value='false', 
        description='Open RViz.'
    )

    use_sim_time_arg = DeclareLaunchArgument(
		'use_sim_time',
		default_value='true',  # Set to 'true' for simulation
		description='Use simulation (Gazebo) clock if true'
	)

    # Visualize in RViz
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', PathJoinSubstitution([
            spot_nav_pkg, 
            'rviz', 
            'dlo.rviz'
        ])],
        condition=IfCondition(LaunchConfiguration('rviz')),
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )

    pointcloud_topic_cfg = LaunchConfiguration('pointcloud_topic', default='/spot/lidar/points')
    declare_pointcloud_topic_arg = DeclareLaunchArgument(
    	'pointcloud_topic',
    	default_value = pointcloud_topic_cfg,
    	description = 'Input point cloud topic name'
    )

    imu_topic_cfg = LaunchConfiguration('imu_topic', default = '/spot/imu')
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
    		('imu'		 , imu_topic_cfg),
    		('pointcloud', pointcloud_topic_cfg),
			('submap'    , 'dlo/odom_node/submap'),
    		('odom'      , 'dlo/odom_node/odom'),
    		('pose'		 , 'dlo/odom_node/pose'),
    		('kfs' 		 , 'dlo/odom_node/odom/keyframe'),
    		('keyframe'	 , 'dlo/odom_node/pointcloud/keyframe')
    	]
    )

    # Event handlers to shutdown if either node exits
    shutdown_on_odom_exit = RegisterEventHandler(
        OnProcessExit(
            target_action=dlo_odom_node,
            on_exit=[Shutdown()]
        )
    )

    return LaunchDescription([
        rviz_arg,
        use_sim_time_arg,
        rviz,
    	declare_pointcloud_topic_arg,
    	declare_imu_topic_arg,
    	dlo_odom_node,
        shutdown_on_odom_exit,
    ])
