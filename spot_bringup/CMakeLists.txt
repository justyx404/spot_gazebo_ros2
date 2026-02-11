cmake_minimum_required(VERSION 3.8)
project(spot_bringup)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(PCL REQUIRED)
find_package(pcl_conversions REQUIRED)

include_directories(${PCL_INCLUDE_DIRS})
link_directories(${PCL_LIBRARY_DIRS})
add_definitions(${PCL_DEFINITIONS})

add_executable(pointcloud_transform src/pointcloud_transform.cpp)
ament_target_dependencies(pointcloud_transform
  rclcpp
  sensor_msgs
  tf2_ros
  tf2_sensor_msgs
  geometry_msgs
)

add_executable(map_publisher src/map_publisher.cpp)
ament_target_dependencies(map_publisher
  rclcpp
  sensor_msgs
  pcl_conversions
  tf2_ros
  geometry_msgs
)
target_link_libraries(map_publisher ${PCL_LIBRARIES})

install(TARGETS pointcloud_transform map_publisher
  DESTINATION lib/${PROJECT_NAME})

install(PROGRAMS
  scripts/thermal_to_rgb.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME thermal_to_rgb
)

install(DIRECTORY launch config rviz maps
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
