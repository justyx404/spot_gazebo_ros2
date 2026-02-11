import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.conditions import IfCondition
from launch_ros.actions import Node, SetParameter

def generate_launch_description():
    pkg_spot_bringup = 'spot_bringup'

    # --- Arguments ---
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time', 
        default_value='true',
        description='Use simulation time'
    )

    config_file_arg = DeclareLaunchArgument(
        'config_file', 
        default_value='far_planner.yaml',
        description='FAR Planner config file name (in spot_bringup/config folder)'
    )

    # Prior map path argument
    prior_map_path_arg = DeclareLaunchArgument(
        'prior_map_path',
        default_value=PathJoinSubstitution([
            get_package_share_directory(pkg_spot_bringup),
            'maps',
            'simple_tunnel.vgh'
        ]),
        description='Path to prior map .vgh file (auto-loaded after 5s delay)'
    )

    # Boolean to enable/disable auto-load
    load_prior_map_arg = DeclareLaunchArgument(
        'load_prior_map',
        default_value='true',
        description='Auto-load prior map on startup'
    )

    # Boolean to enable/disable RViz
    rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value='false',
        description='Launch RViz for visualization'
    )

    # Config Path
    far_planner_config_path = PathJoinSubstitution([
        get_package_share_directory(pkg_spot_bringup),
        'config',
        LaunchConfiguration('config_file')
    ])

    # FAR Planner Node - configured for FAST-LIO odometry
    far_planner_node = Node(
        package='far_planner',
        executable='far_planner',
        name='far_planner',
        output='screen',
        parameters=[
            far_planner_config_path,
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ],
        remappings=[
            # 1. Odometry: Connect FAR to FAST-LIO's odometry
            ('/odom_world', '/odometry_lio'),
            # 2. Global Mapping Input: Use LIO-registered cloud for global map
            ('/terrain_cloud', '/terrain_cloud'), 
            # 3. Dynamic Obstacle Detection Input: Use raw velodyne points
            # ('/scan_cloud', '/velodyne_points'),
            # 4. Local Clearance Check Input: Use the body-frame registered cloud
            ('/terrain_local_cloud', '/terrain_cloud'),
        ]
    )

    # Goal Markers Publisher Node
    goal_markers_node = Node(
        package='spot_navigation',
        executable='publish_goal_markers',
        name='goal_markers_publisher',
        output='screen',
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ]
    )

    # Graph Decoder - used for loading/saving prior maps
    graph_decoder_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            get_package_share_directory('graph_decoder'), 
            '/launch/decoder.launch.py'
        ]),
        launch_arguments={'use_sim_time': LaunchConfiguration('use_sim_time')}.items()
    )

    # Timer to auto-load prior map after graph decoder initializes
    load_prior_map_timer = TimerAction(
        period=5.0,  # Wait 5 seconds for graph decoder to be ready
        actions=[
            ExecuteProcess(
                cmd=[
                    'ros2', 'topic', 'pub', '--once', '/read_file_dir',
                    'std_msgs/msg/String',
                    ['data: ', LaunchConfiguration('prior_map_path')]
                ],
                shell=False,
                output='screen',
                condition=IfCondition(LaunchConfiguration('load_prior_map'))
            )
        ]
    )

    # RViz with navigation config
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', PathJoinSubstitution([
            get_package_share_directory(pkg_spot_bringup),
            'rviz',
            'far_planner.rviz'
        ])],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        condition=IfCondition(LaunchConfiguration('rviz'))
    )

    # Regulated Pure Pursuit Controller (from mpl_planner) - executes the path with velocity regulation
    regulated_pure_pursuit_controller_node = Node(
        package='mpl_planner',
        executable='regulated_pure_pursuit_controller',
        name='regulated_pure_pursuit_controller',
        output='screen',
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
            {'lookahead_distance': 0.5},
            {'linear_velocity': 0.5},              # Max velocity
            {'goal_tolerance': 0.3},                # Goal tolerance
            {'max_angular_velocity': 1.0},          # Max angular velocity
            {'robot_frame': 'base_link'},
            {'curvature_threshold': 0.5},           # Start slowing at this curvature
            {'min_velocity_ratio': 0.3},            # Minimum velocity as ratio of max
            {'deceleration_distance': 0.5},         # Start decelerating this far from goal
            {'use_velocity_regulation': True}       # Enable velocity regulation
        ],
        remappings=[
            ('/local_path', '/far_path')             # Subscribe to FAR Planner's path
        ]
    )

    return LaunchDescription([
        # Sets use_sim_time for all nodes
        SetParameter(name='use_sim_time', value=LaunchConfiguration('use_sim_time')),

        use_sim_time_arg,
        config_file_arg,
        prior_map_path_arg,
        load_prior_map_arg,
        rviz_arg,
        graph_decoder_launch,
        far_planner_node,
        goal_markers_node,
        load_prior_map_timer,
        regulated_pure_pursuit_controller_node,
        rviz_node
    ])
