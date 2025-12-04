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

    # Declare a launch argument for the lidar topic, in case you want to change it easily
    lidar_topic_arg = DeclareLaunchArgument(
        'lidar_topic',
        default_value='/obstacle_cloud',
        description='Topic for the input lidar point cloud'
    )

    local_planner_node = Node(
        package='mpl_planner',
        executable='mpl_planner',
        name='local_planner', # Assign a name to the node
        output='screen',
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')} # Pass the use_sim_time argument
        ],
        remappings=[
            ('/lidar', LaunchConfiguration('lidar_topic')) # Remap /lidar to the specified topic
        ]
    )

    path_follower_node = Node(
        package='mpl_planner',
        executable='pure_pursuit_controller',
        name='pure_pursuit_controller',
        output='screen',
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')} # Pass the use_sim_time argument
        ],
    )

    # Command to publish a zero-velocity message on shutdown
    stop_command = ExecuteProcess(
        cmd=['ros2', 'topic', 'pub', '--once', '/cmd_vel', 'geometry_msgs/msg/Twist', '"{linear: {x: 0.0}, angular: {z: 0.0}}"'],
        shell=True
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
        local_planner_node,
        path_follower_node,
        shutdown_handler
    ])
