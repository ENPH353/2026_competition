#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped
import math

class MoveTruck(Node):
    def __init__(self):
        super().__init__('move_truck')
        self.velocity_publisher_ = self.create_publisher(Twist, "/truck/cmd_vel", 10)
        self.pose_subscriber_ = self.create_subscription(PoseStamped, "/truck/pose", self.control_loop, 10)

        self.waypoints = [(-1.0, 0.0), (-2.0, 0.0), (-1.5, 1.0)]
        self.linear_velocity = 1.0
        self.current_waypoint = 0
        self.last_pose = None

        self.angular_kP = 0.8
        self.distance_threshold = 0.3

    def get_orientation(self, q):
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        return math.atan2(siny_cosp, cosy_cosp)
    
    def control_loop(self, data):
        current_pose = data.pose
        if (self.current_waypoint >= len(self.waypoints)):
            self.current_waypoint = 0

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
            return
        
        # Steering calculation
        target_orientation = math.atan2(target_position_y - current_position_y, target_position_x - current_position_x)
        angle_error = target_orientation - current_orientation
        angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error)) # Normalizing

        move = Twist()
        move.linear.x = self.linear_velocity
        move.angular.z = self.angular_kP * angle_error

        self.velocity_publisher_.publish(move)

def main(args=None):
    rclpy.init(args=args)
    mover = MoveTruck()
    rclpy.spin(mover)
    rclpy.shutdown()

if __name__ == '__main__':
    main()