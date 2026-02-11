from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Declare a launch argument for the lidar topic, in case you want to change it easily
    lidar_topic_arg = DeclareLaunchArgument(
        'lidar_topic',
        default_value='/spot/lidar/points',
        description='Topic for the input lidar point cloud'
    )

    # Declare a launch argument for use_sim_time, as this is often used with Gazebo
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',  # Set to 'true' if running with Gazebo/simulation
        description='Use simulation (Gazebo) clock if true'
    )

    local_planner_node = Node(
        package='local_planner_motion_primitives',
        executable='local_planner',
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
        package='local_planner_motion_primitives',
        executable='pure_pursuit_controller',
        name='pure_pursuit_controller',
        output='screen',
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')} # Pass the use_sim_time argument
        ],
    )

    return LaunchDescription([
        use_sim_time_arg,
        lidar_topic_arg,
        local_planner_node,
        path_follower_node
    ])