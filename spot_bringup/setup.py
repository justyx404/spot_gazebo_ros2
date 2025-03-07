import os
from glob import glob
from setuptools import setup

package_name = 'spot_bringup'

setup(
    name=package_name,
    version='0.0.1',
    packages=['spot_bringup'],  # Changed to match new directory name
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        (os.path.join('share', package_name), ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*.launch.py'))),
        (os.path.join('share', package_name, 'config'), glob(os.path.join('config', '*.yaml'))),
        (os.path.join('share', package_name, 'config'), glob(os.path.join('config', '*.rviz'))),

    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='your_email@example.com',
    description='Spot robot controller with basic stand/sit functionality',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'thermal_to_rgb = spot_bringup.thermal_to_rgb:main',
            # 'spot_controller = spot_ros2_gz_controller.spot_controller:main',
        ],
    },
)