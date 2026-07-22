from glob import glob

from setuptools import find_packages, setup

package_name = 'mini_amr_description'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
    ('share/ament_index/resource_index/packages',
        ['resource/' + package_name]),

    ('share/' + package_name,
        ['package.xml']),

    ('share/' + package_name + '/launch',
        ['launch/display.launch.py']),

    ('share/' + package_name + '/urdf',
        ['urdf/mini_amr.urdf.xacro']),

    # display.launch.py loads rviz/mini_amr.rviz from the package share dir,
    # so the rviz configs must be installed.
    ('share/' + package_name + '/rviz',
        glob('rviz/*.rviz')),
],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jarupat Jaruvatee',
    maintainer_email='jarupatnew2548@gmail.com',
    description='URDF/xacro robot description and RViz configs for the Mini-AMR.',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
