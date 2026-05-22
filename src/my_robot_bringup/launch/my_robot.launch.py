import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node

def generate_launch_description():  
    ld = LaunchDescription()

    # Retrieving directory paths
    my_robot_desc_dir = get_package_share_directory('my_robot_description')
    my_robot_bringup_dir = get_package_share_directory('my_robot_bringup')
    ros_gz_sim_dir = get_package_share_directory('ros_gz_sim')

    # Joining the directory paths with the specific files I want
    urdf_path = os.path.join(my_robot_desc_dir, 'urdf', 'my_robot.urdf.xacro')
    sdf_path = os.path.join(my_robot_bringup_dir, 'world', 'fast_empty.sdf')
    test_sign_path = os.path.join(my_robot_bringup_dir, 'world/models/clue_board', 'clue_board.sdf')
    gazebo_config_path = os.path.join(my_robot_bringup_dir, 'config', 'gazebo_bridge.yaml')
    world_path = os.path.join(my_robot_bringup_dir, 'world')

    # Setting the resource folder to let me use model:// prefix within it
    set_env = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        world_path
    )

    # Booting up Gazebo Harmonic with the fast world .sdf file
    gz_sim = IncludeLaunchDescription( 
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_dir, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': [sdf_path, ' -r']}.items()
    )

    # Setting up the robot state publisher node
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': Command(['xacro ', urdf_path])
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
    sign_poses = [[1, 0, 0, 0],
                  [1.1, 0, 0, 0],
                  [1.2, 0, 0, 0],
                  [1.3, 0, 0, 0],
                  [1.4, 0, 0, 0],
                  [1.5, 0, 0, 0],
                  [1.6, 0, 0, 0],
                  [1.7, 0, 0, 0]]
    
    
    
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
                '-file', test_sign_path,
                '-x', sign_x,
                '-y', sign_y,
                '-z', sign_z,
                '-Y', sign_Y]
        )

        ld.add_action(gz_spawn_signs)
        

    # ROS2 to Gazebo translation node
    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        parameters=[{
            'config_file': gazebo_config_path
        }]
    )

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

    ld.add_action(gz_sim)

    ld.add_action(robot_state_publisher)
    ld.add_action(gz_spawn_robot)
    ld.add_action(gz_bridge)
    
    ld.add_action(truck_mover)
    ld.add_action(yoda_mover) 
    ld.add_action(pedestrian_mover)  
    
    return ld