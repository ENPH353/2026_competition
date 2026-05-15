#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped
import math
import time
from rclpy.signals import SignalHandlerOptions

class MoveTruck(Node):
    def __init__(self):
        super().__init__('move_truck')
        self.velocity_publisher_ = self.create_publisher(Twist, "/truck/cmd_vel", 10)
        self.pose_subscriber_ = self.create_subscription(PoseStamped, "/truck/pose", self.control_loop, 10)

        self.waypoints = [(-2.0, 0.5), (-3, 0.5), (-3.5, 1.0), (-3.5, 1.75), (-3.0, 2.25), (-2.0, 2.25), (-1.5, 1.75), (-1.5, 1.0)]
        self.linear_velocity = 0.5
        self.current_waypoint = 0
        self.last_error = 0
        self.is_shutting_down = False

        self.angular_kP = 1.5
        self.angular_kD = 0.2
        self.distance_threshold = 0.1

    def get_orientation(self, q):
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        return math.atan2(siny_cosp, cosy_cosp)
    
    def stop_robot(self):
        self.is_shutting_down = True
        self.get_logger().info("Shutting down.")
        stop = Twist()
        for _ in range(10):
            self.velocity_publisher_.publish(stop)
            rclpy.spin_once(self, timeout_sec=0.1)
    
    def control_loop(self, data):
        if self.is_shutting_down:
            return
        current_pose = data.pose
        if (self.current_waypoint >= len(self.waypoints)):
            self.current_waypoint = 0
            self.last_error = 0

        # Current positions
        current_position_x = current_pose.position.x
        current_position_y = current_pose.position.y
        current_orientation = self.get_orientation(current_pose.orientation)

        # Goal positions
        target_position_x, target_position_y = self.waypoints[self.current_waypoint]

        # Implementing a basic Pure Pursuit algorithim
        distance = math.sqrt((target_position_x - current_position_x)**2 + (target_position_y - current_position_y)**2)

        if (distance < self.distance_threshold):
            self.current_waypoint += 1
            self.get_logger().info("Switching to next waypoint: " + str(self.current_waypoint))
            self.last_error = 0
            return
        
        # Steering calculation
        target_orientation = math.atan2(target_position_y - current_position_y, target_position_x - current_position_x)
        angle_error = target_orientation - current_orientation
        angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error)) # Normalizing

        move = Twist()
        move.linear.x = self.linear_velocity
        if (self.last_error != 0):
            move.angular.z = self.angular_kP * angle_error + self.angular_kD * (angle_error - self.last_error)**2
        else:
            move.angular.z = self.angular_kP * angle_error
        
        self.last_error = angle_error

        self.velocity_publisher_.publish(move)

def main(args=None):
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    mover = MoveTruck()
    try:
        rclpy.spin(mover)
    except KeyboardInterrupt:
        mover.get_logger().info("Shut command recieved")
    finally:
        mover.stop_robot()
        mover.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()