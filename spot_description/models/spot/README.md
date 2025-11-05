# Notes on the publish frequency on the robot states

This section lists the publication frequencies of various robot states and
sensors in the Spot Gazebo simulation.

## Robot States

* Joint State Publisher (Gazebo plugin, `/model/spot/joint_state`): 200 Hz
* Odometry Publisher (Gazebo plugin, `/model/spot/odometry`): 10 Hz

## Sensors

* Lidar (`/spot/lidar/scan`, `/spot/lidar/points`): 10 Hz
* Thermal Camera (`/spot/camera/thermal_camera`): 30 Hz
* Fisheye Cameras (back, front-left, front-right, left, right): 30 Hz
* IMU (`/spot/imu`): 100 Hz
