import sys
import random

from pathlib import Path
from ament_index_python.packages import get_package_share_directory, get_package_prefix
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node

def generate_launch_description():  
    ld = LaunchDescription()

    # Retrieving directory paths
    my_robot_desc_dir = Path(get_package_share_directory('my_robot_description'))
    my_robot_bringup_dir = Path(get_package_share_directory('my_robot_bringup'))
    ros_gz_sim_dir = Path(get_package_share_directory('ros_gz_sim'))
    custom_plugins_path = Path(get_package_prefix('custom_plugins')) / 'lib'

    # Joining the directory paths with the specific files I want
    urdf_path = my_robot_desc_dir / 'urdf' / 'my_robot.urdf.xacro'
    sdf_path = my_robot_bringup_dir / 'world' / 'fast_empty.sdf'
    gazebo_config_path = my_robot_bringup_dir / 'config' / 'gazebo_bridge.yaml'
    gui_config_path = my_robot_bringup_dir / 'config' / 'keypublisher.config'
    world_path = my_robot_bringup_dir / 'world'

    clueboard_generator_path = world_path / "clueboard_scripts"
    
    if clueboard_generator_path.as_posix() not in sys.path:
        sys.path.append(clueboard_generator_path.as_posix())
    import clueboard_generator 

    # Setting the resource folder to let me use model:// prefix within it
    set_env = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        world_path.as_posix()
    )

    # Loading in plugin path
    set_plugin_path = AppendEnvironmentVariable(
        'GZ_SIM_SYSTEM_PLUGIN_PATH',
        (custom_plugins_path).as_posix()
    )
    
    # Booting up Gazebo Harmonic with the fast world .sdf file
    gz_sim = IncludeLaunchDescription( 
        PythonLaunchDescriptionSource(
            (ros_gz_sim_dir / 'launch' / 'gz_sim.launch.py').as_posix() # Adding .as_posix() converts the path type objects to string
        ),
        launch_arguments={'gz_args': [sdf_path.as_posix(), ' -r', f' --gui-config {gui_config_path.as_posix()}']}.items()
    )

    # Setting up the robot state publisher node
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': Command(['xacro ', urdf_path.as_posix()])
        }]
    )

     # ROS2 to Gazebo translation node
    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        parameters=[{
            'config_file': gazebo_config_path.as_posix()
        }]
    )

    # Spawning in the robot
    gz_spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-topic', 'robot_description',
            '-x', '-5.5',  
            '-y', '-2.5', 
            '-z', '0.1',  
            '-Y', '1.57']
    )

    # Spawning in the signs
    num_signs = 8
    max_pitch = 0.15
    sign_poses = [[-5.81, -1.64, 0.04, 3.14 + random.uniform(-max_pitch, max_pitch)], # First sign (fixed)
                  [-5.16, random.uniform(1.11, 1.6), 0.04, 3.14 + random.uniform(-max_pitch, max_pitch)], # Second sign (y-varying)
                  [-4.0, 1.67, 0.04, 1.57 + random.uniform(-max_pitch, max_pitch)], # Third sign (fixed)
                  [-0.83, random.uniform(0.63, 0), 0.04, 0 + random.uniform(-max_pitch, max_pitch)], # Fourth sign (y-varying)
                  [-0.83, random.uniform(-1.84, -1.44), 0.04, 3.14 + random.uniform(-max_pitch, max_pitch)], # Fifth sign (y-varying)
                  [random.uniform(3.0, 3.41), -1.71, 0.04, 1.57 + random.uniform(-max_pitch, max_pitch)], # Sixth sign (x-varying)
                  [3.8, 2.01, 0.04, -1.57 + random.uniform(-max_pitch, max_pitch)], # Seventh sign (fixed)
                  [0.9, 1.2, 1.86, -1.57 + random.uniform(-max_pitch, max_pitch)]] # Eigth sign (fixed)
    
    clueboard_paths = clueboard_generator.main()
    
    for i in range(num_signs):

        sign_name = f"sign_{i}"
        sign_x = str(sign_poses[i][0])
        sign_y = str(sign_poses[i][1])
        sign_z = str(sign_poses[i][2])
        sign_Y = str(sign_poses[i][3])

        gz_spawn_signs = Node(
            package='ros_gz_sim',
            executable='create',
            output='screen',
            arguments=['-name', sign_name,
                '-file', clueboard_paths[i],
                '-x', sign_x,
                '-y', sign_y,
                '-z', sign_z,
                '-Y', sign_Y]
        )

        ld.add_action(gz_spawn_signs)

    # NPC nodes
    truck_mover = Node(  
        package="bringup_nodes", 
        executable="move_truck",
        output='screen' 
    )  

    yoda_mover = Node(  
        package="bringup_nodes", 
        executable="move_yoda" ,
        output='screen'
    )  

    pedestrian_mover = Node(  
        package="bringup_nodes", 
        executable="move_pedestrian",
        output='screen' 
    )  
    
    ld.add_action(set_env)
    ld.add_action(set_plugin_path)

    ld.add_action(gz_sim)

    ld.add_action(robot_state_publisher)
    ld.add_action(gz_spawn_robot)
    ld.add_action(gz_bridge)
    
    ld.add_action(truck_mover)
    ld.add_action(yoda_mover) 
    ld.add_action(pedestrian_mover)  
    
    return ld