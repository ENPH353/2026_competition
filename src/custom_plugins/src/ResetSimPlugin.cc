#include "custom_plugins/ResetSimPlugin.hh" // Include the ResetSimPlugin header file here
#include <gz/plugin/Register.hh>
#include <gz/sim/components/Model.hh>
#include <gz/sim/components/Name.hh>
#include <gz/sim/components/Pose.hh>
#include <gz/math/Pose3.hh>

#include <gz/common/Console.hh>

using namespace reset_plugin;

void ResetSimPlugin::Reset(const gz::sim::UpdateInfo &_info, gz::sim::EntityComponentManager &_ecm)
{   
    gzerr << "[ResetSimPlugin] Reset triggered! Searching for my_robot..." << std::endl;

    // 1. Search specifically for the name we found in the inventory check
    std::string my_robot_name = "my_robot"; 
    
    gz::sim::Entity robot_entity = _ecm.EntityByComponents(
        gz::sim::components::Model(),
        gz::sim::components::Name(my_robot_name) 
    );

    // 2. If we found it, teleport it!
    if (robot_entity != gz::sim::kNullEntity) 
    {
        // Your Python launch file coordinates
        gz::math::Pose3d spawn_pose(-5.5, -2.5, 0.1, 0.0, 0.0, 1.57);

        // 3. THE SECRET SAUCE: SetComponentData
        // This updates the position AND tells the physics engine to pay attention
        _ecm.SetComponentData<gz::sim::components::Pose>(robot_entity, spawn_pose);
        
        gzerr << "[ResetSimPlugin] SUCCESS: Teleported '" << my_robot_name << "' back to spawn!" << std::endl;
    }
    else 
    {
        gzerr << "[ResetSimPlugin] FAILURE: Could not find '" << my_robot_name << "'!" << std::endl;
    }

}

GZ_ADD_PLUGIN (
    reset_plugin::ResetSimPlugin,
    gz::sim::System,
    ResetSimPlugin::ISystemReset
)