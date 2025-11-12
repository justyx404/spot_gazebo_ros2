from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler, Shutdown, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    spot_nav_pkg = FindPackageShare('spot_navigation')

    rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value='true', 
        description='Open RViz.'
    )

    use_sim_time_arg = DeclareLaunchArgument(
		'use_sim_time',
		default_value='true',
		description='Use simulation (Gazebo) clock if true'
	)

    map_path_arg = DeclareLaunchArgument(
        'map_path',
        default_value='simple_tunnel.pcd',
        description='Filename of the map file (e.g., simple_tunnel.pcd).'
    )

    # Visualize in RViz
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', PathJoinSubstitution([
            spot_nav_pkg, 
            'rviz', 
            'dlo_localization.rviz',
        ])],
        condition=IfCondition(LaunchConfiguration('rviz')),
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )

    dlo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                spot_nav_pkg,
                'launch',
                'dlo.launch.py'
            ])
        ),
        launch_arguments={
            'rviz': 'false',
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }.items()
    )

    dlo_yaml_path = PathJoinSubstitution([spot_nav_pkg, 'config', 'dlo.yaml'])
    localization_yaml_path = PathJoinSubstitution([spot_nav_pkg, 'config', 'localization.yaml'])

    dlo_localization_node = Node(
        name = 'dlo_localization',
        package = 'direct_lidar_odometry',
        executable = 'dlo_localization_node',
        output = 'screen',
        parameters = [
            dlo_yaml_path,
            localization_yaml_path,
            {
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'dlo/localizationNode/map_path': PathJoinSubstitution([spot_nav_pkg, 'maps', LaunchConfiguration('map_path')])
            }
        ],
        remappings= [
            ('global_map'         , 'dlo/localization_node/global_map'),
            ('global_map_filtered', 'dlo/localization_node/global_map_filtered'),
            ('pointcloud', '/dlo/odom_node/pointcloud/keyframe'),
            ('odom'      , 'dlo/odom_node/odom'),
        ]
	)

    shutdown_on_localization_exit = RegisterEventHandler(
        OnProcessExit(
            target_action=dlo_localization_node,
            on_exit=[Shutdown()]
        )
    )

    return LaunchDescription([
        rviz_arg,
        use_sim_time_arg,
        map_path_arg,
        rviz,
        dlo_launch,
        dlo_localization_node,
        shutdown_on_localization_exit
    ])
