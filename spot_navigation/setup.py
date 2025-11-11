import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'spot_navigation'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
        (os.path.join('share', package_name, 'maps'), glob('maps/*.pcd')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Yixiang Gao',
    maintainer_email='ygao@mst.edu',
    description='Config files for using the navigation stack',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)
