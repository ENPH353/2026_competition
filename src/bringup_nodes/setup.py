from setuptools import find_packages, setup

package_name = 'bringup_nodes'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='fizzer',
    maintainer_email='taigasery78@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            "move_truck = bringup_nodes.truck_circuit:main",
            "move_yoda = bringup_nodes.baby_yoda_circuit:main",
            "move_pedestrian = bringup_nodes.pedestrian_circuit:main"
        ],
    },
)
