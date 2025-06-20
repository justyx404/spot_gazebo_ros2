from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    spot_nav_pkg = FindPackageShare('spot_navigation')
    spot_bringup_pkg = FindPackageShare('spot_bringup')

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',  # Set to 'true' for simulation
        description='Use simulation (Gazebo) clock if true'
    )

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

    local_planner_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([spot_nav_pkg, 'launch', 'planner.launch.py'])
        ]),
    )

    # Launch RViz
    rviz_config_path = PathJoinSubstitution([spot_nav_pkg, 'config', 'spot_nav_obstacle_avoidance.rviz'])
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )

    return LaunchDescription([
        use_sim_time_arg,
        spot_gazebo_launch,
        dlo_launch,
        lidar_localization_launch,
        local_planner_launch,
        rviz_node
    ]) 