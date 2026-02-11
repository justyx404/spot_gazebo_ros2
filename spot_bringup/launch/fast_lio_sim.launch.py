from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    pkg_spot_bringup = "spot_bringup"

    # Arguments
    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
        description="Use simulation (Gazebo) time if true",
    )

    config_file_arg = DeclareLaunchArgument(
        "config_file",
        default_value="lio_localization.yaml",
        description="Config file name (in spot_bringup/config folder)",
    )

    map_file_path_arg = DeclareLaunchArgument(
        "map_file_path",
        default_value="scans.pcd",
        description="Output PCD filename (saved to fast_lio/pcd/)",
    )

    max_range_arg = DeclareLaunchArgument(
        "max_range",
        default_value="30.0",
        description="Max point range in meters (preprocess filter)",
    )

    rviz_arg = DeclareLaunchArgument(
        "rviz", default_value="false", description="Start RViz"
    )

    # Config path
    config_path = PathJoinSubstitution(
        [
            get_package_share_directory(pkg_spot_bringup),
            "config",
            LaunchConfiguration("config_file"),
        ]
    )

    # FAST-LIO (SLAM/Mapping Mode) - publishes /Odometry, /cloud_registered, and builds local map
    fast_lio_node = Node(
        package="fast_lio",
        executable="fastlio_mapping",
        name="fastlio_mapping",
        output="screen",
        parameters=[
            config_path,
            {
                "use_sim_time": LaunchConfiguration("use_sim_time"),
                "publish.map_en": True,
                "pcd_save.pcd_save_en": True,
                "mapping.extrinsic_est_en": False,
                "publish.scan_publish_en": True,
                "publish.scan_bodyframe_pub_en": True,
                "publish.dense_publish_en": True,
                # Better filter settings for map quality
                "filter_size_surf": 0.3,       # scan downsample voxel (default 0.5)
                "filter_size_map": 0.3,         # map voxel resolution (default 0.5)
                "point_filter_num": 1,          # keep all points (default 2 = every 2nd)
                "map_file_path": LaunchConfiguration("map_file_path"),
                "preprocess.max_range": LaunchConfiguration("max_range"),
            },
        ],
        remappings=[("/Odometry", "/odometry_lio")],
    )

    # RViz
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=[
            "-d",
            PathJoinSubstitution(
                [get_package_share_directory("fast_lio"), "rviz", "fastlio.rviz"]
            ),
        ],
        parameters=[{"use_sim_time": LaunchConfiguration("use_sim_time")}],
        condition=IfCondition(LaunchConfiguration("rviz")),
    )

    return LaunchDescription(
        [
            use_sim_time_arg,
            config_file_arg,
            map_file_path_arg,
            max_range_arg,
            rviz_arg,
            fast_lio_node,
            rviz_node,
        ]
    )
