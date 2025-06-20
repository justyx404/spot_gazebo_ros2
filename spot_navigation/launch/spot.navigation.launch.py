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
        default_value='true',  # Set to 'true' for simulation
        description='Use simulation (Gazebo) clock if true'
    )

    # Include Spot Gazebo Simulation launch file
    spot_gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([spot_bringup_pkg, 'launch', 'spot.gazebo.launch.py'])
        ]),
        launch_arguments={
            'rviz': 'false',
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }.items()
    )

    # Include DLO odometry launch file
    dlo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([spot_nav_pkg, 'launch', 'dlo.launch.py'])
        ]),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }.items()
    )

    # Include lidar localization launch file
    lidar_localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([spot_nav_pkg, 'launch', 'lidar_localization.launch.py'])
        ]),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }.items()
    )

    local_planner_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([spot_nav_pkg, 'launch', 'planner.launch.py'])
        ]),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'lidar_topic': '/spot/lidar/points'  # Default lidar topic, can be overridden
        }.items()
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