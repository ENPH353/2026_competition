from setuptools import find_packages, setup

package_name = 'score_tracker_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name, ['score_tracker_pkg/score_tracker.py', 'score_tracker_pkg/score_tracker.ui',
                                   'score_tracker_pkg/ENPHLogo.jpg', 'score_tracker_pkg/FIZZ_CLUE.svg']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='fizzer',
    maintainer_email='miti@phas.ubc.ca',
    description='TODO: Package description',
    license='TODO: License declaration',
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
