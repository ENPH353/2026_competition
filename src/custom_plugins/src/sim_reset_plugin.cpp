#include <thread>
#include <memory>
#include <string>

// ROS 2 Headers
#include <rclcpp/rclcpp.hpp>
#include <std_srvs/srv/empty.hpp>
#include <std_msgs/msg/empty.hpp>

// Gazebo Headers
#include <gz/sim/System.hh>
#include <gz/sim/World.hh>
#include <gz/plugin/Register.hh>
#include <gz/transport/Node.hh>

// Gazebo Messages (Protobuf)
#include <gz/msgs/world_control.pb.h>
#include <gz/msgs/world_reset.pb.h>

namespace simulation_reset_plugin
{

class SimResetPlugin : 
  public gz::sim::System,
  public gz::sim::ISystemConfigure
{
private:
  // ROS 2 variables
  rclcpp::Node::SharedPtr ros_node_;
  rclcpp::Service<std_srvs::srv::Empty>::SharedPtr reset_service_;
  rclcpp::Publisher<std_msgs::msg::Empty>::SharedPtr npc_reset_pub_;
  std::thread ros_thread_;

  // Gazebo variables
  gz::transport::Node gz_node_;
  gz::transport::Node::Publisher gz_control_pub_;

public:
  SimResetPlugin() = default;

  ~SimResetPlugin() override {
    // Clean up the ROS 2 thread when the simulation closes
    if (rclcpp::ok()) {
      rclcpp::shutdown();
    }
    if (ros_thread_.joinable()) {
      ros_thread_.join();
    }
  }

  // Runs exactly once when the <world> loads
  void Configure(const gz::sim::Entity &_entity,
                 const std::shared_ptr<const sdf::Element> &_sdf,
                 gz::sim::EntityComponentManager &_ecm,
                 gz::sim::EventManager &_eventMgr) override 
  {
    // 1. Get the world name to set up the Gazebo publisher
    gz::sim::World world(_entity);
    std::string world_name = world.Name(_ecm);
    std::string control_topic = "/world/" + world_name + "/control";
    
    // Advertise the native Gazebo topic that controls physics state
    gz_control_pub_ = gz_node_.Advertise<gz::msgs::WorldControl>(control_topic);

    // 2. Initialize ROS 2
    if (!rclcpp::ok()) {
      rclcpp::init(0, nullptr);
    }
    ros_node_ = rclcpp::Node::make_shared("gazebo_world_reset_node");

    // 3. Set up the ROS 2 Service (The trigger)
    reset_service_ = ros_node_->create_service<std_srvs::srv::Empty>(
      "/trigger_sim_reset",
      std::bind(&SimResetPlugin::OnResetTriggered, this, std::placeholders::_1, std::placeholders::_2)
    );

    // 4. Set up the ROS 2 Publisher (The alert for NPCs)
    npc_reset_pub_ = ros_node_->create_publisher<std_msgs::msg::Empty>("/npc_reset_alert", 10);

    // 5. Spin ROS 2 in a separate background thread so it doesn't freeze Gazebo
    ros_thread_ = std::thread([this]() {
      rclcpp::spin(this->ros_node_);
    });

    RCLCPP_INFO(ros_node_->get_logger(), "Simulation Reset Plugin Loaded! Listening on /trigger_sim_reset");
  }

private:
  // This callback fires whenever you call the /trigger_sim_reset ROS service
  void OnResetTriggered(const std::shared_ptr<std_srvs::srv::Empty::Request> /*req*/,
                        std::shared_ptr<std_srvs::srv::Empty::Response> /*res*/)
  {
    RCLCPP_INFO(ros_node_->get_logger(), "Reset triggered! Rewinding physics and alerting NPCs...");

    // 1. Tell Gazebo to reset time, teleport models, and clear velocities
    gz::msgs::WorldControl control_msg;
    control_msg.mutable_reset()->set_all(true); 
    gz_control_pub_.Publish(control_msg);

    // 2. Broadcast the alert so your external NPC Python/C++ nodes know to reset their logic
    std_msgs::msg::Empty alert_msg;
    npc_reset_pub_->publish(alert_msg);
  }
};

} // namespace simulation_reset_plugin

// Register the plugin with Gazebo
GZ_ADD_PLUGIN(
  simulation_reset_plugin::SimResetPlugin,
  gz::sim::System,
  simulation_reset_plugin::SimResetPlugin::ISystemConfigure
)