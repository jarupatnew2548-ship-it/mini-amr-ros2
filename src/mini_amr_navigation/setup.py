from glob import glob

from setuptools import find_packages, setup

package_name = 'mini_amr_navigation'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),

    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/mini_amr_navigation']),

        ('share/mini_amr_navigation',
            ['package.xml']),

        ('share/mini_amr_navigation/launch',
            ['launch/navigation.launch.py']),
        
        ('share/mini_amr_navigation/config',
            ['config/nav2_params.yaml']),

        ('share/mini_amr_navigation/rviz',
            ['rviz/nav2.rviz', 'rviz/slam.rviz']),

        ('share/mini_amr_navigation/maps',
            glob('maps/*.yaml') + glob('maps/*.pgm')),
    ],

    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jarupat Jaruvatee',
    maintainer_email='jarupatnew2548@gmail.com',
    description='Nav2 map-based navigation (localization, planning and control) '
                'for the simulated Mini-AMR.',
    license='Apache-2.0',

    extras_require={
        'test': [
            'pytest',
        ],
    },

    entry_points={
        'console_scripts': [
            'nav_demo_recorder = mini_amr_navigation.nav_demo_recorder:main',
        ],
    },
)