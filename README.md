
# 2026 Fizz Detective Competition [IN PROGRESS]

This repository contains the following ROS2 packages within the src/ folder:

| Packages | Description |
| :--- | :--- |
| bringup_nodes | Contains ROS2 control script nodes for NPCs. |
| custom_plugins | Contains a C++ Gazebo world level plugin that resets non-static entities by teleporting them back to their spawnpoints. |
| my_robot_bringup | Contains the launch file and gazebo-to-ROS2 config files. |
| score_tracker_pkg | Contains the clue board score tracking system. |
| world_pkg | Describes the simulation world and its associated assets. |
| my_robot_pkg | [EXPECTED] This is not contained in the competition repository. A default differential drive URDF robot that students can modify and control is provided [here](https://github.com/ENPH353/my_robot_pkg). This package should be saved in ```2026_competition_ws/src``` folder.|

## Setup instructions

**Pre-requisites: Ubuntu 24.04, ROS2 Jazzy, and Gazebo Harmonic.**

- Make the ROS2 workspace folder. This folder will become the competition ROS2 workspace:
```
mkdir -p ~/2026_competition_ws/src
cd ~/2026_competition_ws/src
```

- Clone the repository's contents inside the workspace:
```
git clone https://github.com/ENPH353/2026_competition.git
```
NOTE: The competition repository requires a robot URDF package named ```my_robot_pkg```. To start with clone the default repository as follows:
```
cd ~/2026_competition_ws/src
git clone https://github.com/ENPH353/my_robot_pkg.git
```

- Build the ROS2 workspace using colcon with symbolic links (allows for editing files without rebuilding after every change):
```
cd ~/2026_competition_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install 
```

## Starting and stopping the competition

- To start the competition world inside the Gazebo simulator, you must first source the ROS2 competition workspace:
```
source install/setup.bash
```

- Then run the launch file that starts Gazebo and spawns in the world assets:
```
ros2 launch my_robot_bringup my_robot.launch.py
```

<br>

- To close the simulation, inside the terminal where you launched from, run *ctrl+c* or create an alias that you can run later that kills all Gazebo and ROS2 processes:
```
alias kill-gz="pkill -f 'gz sim'; pkill -f 'gz sim server'; pkill -f 'gzsim gui'; pkill -9 -f 'ros_gz_bridge'; pkill -9 -f 'ros2 launch'"
```
To use the command without restarting the terminal, source first and then run the alias:
```
source ~/.bashrc
kill-gz
```
<br>

- **(NOT REQUIRED)** If you find that the Gazebo simulation window is too big for your screen, close the simulation and then in the same terminal where you launched it, run the following command.
```
export QT_SCALE_FACTPR=0.8
```
 This command sets the terminal environment variable which scales the user interface of QT based applications down to 80% their original size.
