import yaml
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node, SetParameter
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import PythonExpression
import launch_ros

def generate_launch_description():
    return LaunchDescription([
        SetParameter(name='use_sim_time', value='true'),
        DeclareLaunchArgument('config', default_value='default'),

        Node(
            package='far_planner',
            executable='far_planner',
            name='far_planner',
            output='screen',
            parameters=[
                PythonExpression([
                '"', 
                get_package_share_directory('far_planner'), 
                '/config/', 
                LaunchConfiguration('config'), 
                '.yaml"'])
            ],
            remappings=[
                ('/odom_world', '/dlo/odom_node/odom'),
                ('/terrain_local_cloud', '/dlo/odom_node/pointcloud/keyframe'),
                ('/terrain_cloud', '/dlo/localization_node/global_map'),
                ('/scan_cloud', '/spot/lidar/points'),
            ]
        ),
        
        Node(
            package='rviz2',
            executable='rviz2',
            name='far_rviz',
            arguments=['-d', 
                PythonExpression([
                '"', 
                get_package_share_directory('far_planner'), 
                '/rviz/', 
                LaunchConfiguration('config'), 
                '.rviz"'])
            ],
            respawn=False,
        ),

        # Including another launch file
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([get_package_share_directory('graph_decoder'), '/launch/decoder.launch.py'])
        )
    ])
