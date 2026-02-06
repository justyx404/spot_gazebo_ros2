from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
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

    map_file_path = PathJoinSubstitution([spot_nav_pkg, 'maps', LaunchConfiguration('map_path')])

    # Publish Map PCD and Static TF (map -> odom_lidar)
    # Using custom node in spot_bringup
    map_publisher_node = Node(
        package='spot_bringup',
        executable='map_publisher',
        name='map_publisher',
        parameters=[{
            'map_path': map_file_path,
            'leaf_size': 0.25,
            'ransac_threshold': 0.15,
            'publish_rate': 5.0,
            'frame_id': 'map',
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }],
        output='screen'
    )

    return LaunchDescription([
        rviz_arg,
        use_sim_time_arg,
        map_path_arg,
        rviz,
        dlo_launch,
        map_publisher_node
    ])
