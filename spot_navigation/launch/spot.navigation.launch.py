from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    spot_nav_pkg = FindPackageShare('spot_navigation')
    spot_bringup_pkg = FindPackageShare('spot_bringup')

    # Include Spot Gazebo launch file
    spot_gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([spot_bringup_pkg, 'launch', 'spot.gazebo.launch.py'])
        ]),
        launch_arguments={
            'rviz': 'false'
        }.items()
    )

    # Include DLO launch file
    dlo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([spot_nav_pkg, 'launch', 'dlo.launch.py'])
        ])
    )

    # Include lidar localization launch file
    lidar_localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([spot_nav_pkg, 'launch', 'lidar_localization.launch.py'])
        ])
    )

    # Launch RViz
    rviz_config_path = PathJoinSubstitution([spot_nav_pkg, 'config', 'spot_navigation.rviz'])
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path],
        parameters=[{'use_sim_time': True}],
    )

    return LaunchDescription([
        spot_gazebo_launch,
        dlo_launch,
        lidar_localization_launch,
        rviz_node
    ]) 