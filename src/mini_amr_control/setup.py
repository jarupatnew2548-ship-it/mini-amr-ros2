from setuptools import find_packages, setup

package_name = 'mini_amr_control'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jarupat Jaruvatee',
    maintainer_email='jarupatnew2548@gmail.com',
    description='Motion control and simulated odometry nodes for the Mini-AMR.',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'fake_odom_publisher = mini_amr_control.fake_odom_publisher:main',
            'mecanum_kinematics_node = mini_amr_control.mecanum_kinematics_node:main',
	    'tf_broadcaster = mini_amr_control.tf_broadcaster:main',
        ],
    },
)
