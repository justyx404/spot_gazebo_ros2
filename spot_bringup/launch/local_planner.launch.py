from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler, ExecuteProcess
from launch.event_handlers import OnShutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Declare a launch argument for use_sim_time, as this is often used with Gazebo
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',  # Set to 'true' if running with Gazebo/simulation
        description='Use simulation (Gazebo) clock if true'
    )

    # Declare a launch argument for the lidar topic
    # Using /spot/lidar/points_base as it is already transformed to base_link
    lidar_topic_arg = DeclareLaunchArgument(
        'lidar_topic',
        default_value='/spot/lidar/points_base',
        description='Topic for the input point cloud (converted to base_link)'
    )

    # Declare a launch argument for the odom topic
    # Using /dlo/odom_node/odom as specified by the user
    odom_topic_arg = DeclareLaunchArgument(
        'odom_topic',
        default_value='/dlo/odom_node/odom',
        description='Topic for the robot odometry'
    )

    map_server_node = Node(
        package='mpl_planner',
        executable='mpl_map_server_node',
        name='mpl_map_server_node',
        output='screen',
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ],
        remappings=[
            ('pointcloud', LaunchConfiguration('lidar_topic')),
            ('odom', LaunchConfiguration('odom_topic'))
        ]
    )

    local_planner_node = Node(
        package='mpl_planner',
        executable='mpl_planner',
        name='local_planner', # Assign a name to the node
        output='screen',
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')} # Pass the use_sim_time argument
        ],
        # The node subscribes to /obstacle_cloud by default
    )

    path_follower_node = Node(
        package='mpl_planner',
        executable='regulated_pure_pursuit_controller',
        name='pure_pursuit_controller',
        output='screen',
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')} # Pass the use_sim_time argument
        ],
    )

    # Command to publish a zero-velocity message on shutdown
    stop_command = ExecuteProcess(
        cmd=[
            'ros2', 'topic', 'pub', '--once', 
            '/cmd_vel', 
            'geometry_msgs/msg/Twist', 
            '{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}'
        ],
        output='screen'
    )

    # Register the stop command to run on shutdown
    shutdown_handler = RegisterEventHandler(
        event_handler=OnShutdown(
            on_shutdown=[stop_command],
        )
    )

    return LaunchDescription([
        use_sim_time_arg,
        lidar_topic_arg,
        odom_topic_arg,
        map_server_node,
        local_planner_node,
        path_follower_node,
        shutdown_handler
    ])
