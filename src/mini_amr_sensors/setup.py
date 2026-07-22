from glob import glob

from setuptools import find_packages, setup

package_name = 'mini_amr_sensors'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/rviz', glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jarupat Jaruvatee',
    maintainer_email='jarupatnew2548@gmail.com',
    description='Simulated LiDAR and safety-zone sensor nodes for the Mini-AMR.',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'scan_analyzer_node = mini_amr_sensors.scan_analyzer_node:main',
            'fake_scan_publisher = mini_amr_sensors.fake_scan_publisher:main',
            'tf_broadcaster = mini_amr_sensors.tf_broadcaster:main',
            'safety_zone_marker = mini_amr_sensors.safety_zone_marker:main',
        ],
    },
)
