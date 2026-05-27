#include "custom_plugins/ResetSimPlugin.hh" // Include the ResetSimPlugin header file here
#include <gz/plugin/Register.hh>
#include <gz/sim/components/Model.hh>
#include <gz/sim/components/Name.hh>
#include <gz/sim/components/Pose.hh>
#include <gz/math/Pose3.hh>
#include <gz/sim/components/PoseCmd.hh>

#include <gz/common/Console.hh>

using namespace reset_plugin; // Lets me use reset_plugin methods without having to write reset_plugin:: every time

// Good practice to comment out passed in variables we won't use to stop the compiler from throwing warnings
void ResetSimPlugin::Configure(const gz::sim::Entity &/*_entity*/,
                               const std::shared_ptr<const sdf::Element> &/*_sdf*/,
                               gz::sim::EntityComponentManager &/*_ecm*/,
                               gz::sim::EventManager &/*_eventMgr*/)
{   
    // Subscribe to the GUI's keystroke topic
    if (this->node.Subscribe("/keyboard/keypress", &ResetSimPlugin::OnKeyPress, this))
    {
        gzerr << "[ResetSimPlugin] Successfully subscribed to keyboard events!" << std::endl;
    }
    else
    {
        gzerr << "[ResetSimPlugin] Failed to subscribe to keyboard topic." << std::endl;
    }
}

void ResetSimPlugin::OnKeyPress(const gz::msgs::Int32 &_msg)
{
    // ASCII value for r and R
    if (_msg.data() == 114 || _msg.data() == 82) 
    {   
        // gzerr << "Key pressed! Updating flag on object at: " << this << std::endl;
        this->teleport_requested = true;
    }
}

void ResetSimPlugin::PreUpdate(const gz::sim::UpdateInfo &/*_info*/, gz::sim::EntityComponentManager &_ecm)
{   
    // Check if no teleport was requested
    if (!this->teleport_requested)
    {
        return;
    }

    // Find the robot
    std::string my_robot_name = "my_robot"; 
    gz::sim::Entity robot_entity = _ecm.EntityByComponents(
        gz::sim::components::Model(),
        gz::sim::components::Name(my_robot_name) 
    );

    // Teleport the robot back to spawn
    if (robot_entity != gz::sim::kNullEntity) 
    {
        gz::math::Pose3d spawn_pose(-5.5, -2.5, 0.1, 0.0, 0.0, 1.57);
        _ecm.SetComponentData<gz::sim::components::WorldPoseCmd>(robot_entity, spawn_pose);
    }
    else 
    {
        gzerr << "[ResetSimPlugin] Keystroke Reset Failed: Robot not found in ECM!" << std::endl;
    }

    // Reset the flag so we don't teleport on the next frame
    this->teleport_requested = false;
}

GZ_ADD_PLUGIN (
    reset_plugin::ResetSimPlugin,
    gz::sim::System,
    gz::sim::ISystemConfigure,
    gz::sim::ISystemPreUpdate
)