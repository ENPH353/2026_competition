#include "custom_plugins/ResetSimPlugin.hh" // Include the ResetSimPlugin header file here
#include <gz/plugin/Register.hh>
#include <gz/sim/components/Model.hh>
#include <gz/sim/components/Name.hh>
#include <gz/sim/components/Pose.hh>
#include <gz/math/Pose3.hh>
#include <gz/sim/components/PoseCmd.hh>
#include <gz/sim/components/World.hh>
#include <gz/sim/components/Joint.hh>
#include <gz/sim/components/ParentEntity.hh>
#include <gz/sim/components/JointPositionReset.hh>
#include <gz/sim/components/JointVelocityReset.hh>
#include <gz/sim/components/Static.hh>

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
    if (!this->memory_locked)
    {
        _ecm.Each<gz::sim::components::Model, gz::sim::components::Pose, gz::sim::components::Name>(
            [&](const gz::sim::Entity &_modelEntity,
                const gz::sim::components::Model *,
                const gz::sim::components::Pose *_poseComp,
                const gz::sim::components::Name *_nameComp) -> bool
            {
                // 1. Is this a NEW robot we haven't seen yet?
                if (this->initial_poses.find(_modelEntity) == this->initial_poses.end())
                {
                    const auto *staticComp = _ecm.Component<gz::sim::components::Static>(_modelEntity);
                    bool is_static = staticComp ? staticComp->Data() : false;

                    if (!is_static) 
                    {
                        this->initial_poses[_modelEntity] = _poseComp->Data();
                        gzerr << "[ResetSimPlugin] Memorized initial spawn pose for: " 
                              << _nameComp->Data() << std::endl;
                    }
                }
                // 2. We ALREADY memorized this robot. Let's check if it started moving.
                else 
                {
                    // Calculate the distance between its current pose and its spawn pose
                    double distance = _poseComp->Data().Pos().Distance(this->initial_poses[_modelEntity].Pos());
                    
                    // If it moved more than 5 cm (0.05 meters)...
                    if (distance > 0.05) 
                    {
                        this->memory_locked = true; // LOCK THE MEMORY BANK
                        gzerr << "[ResetSimPlugin] Agent movement detected! Memory bank permanently locked to save CPU." << std::endl;
                        
                        return false; // Returning false breaks us out of the ECM.Each loop early!
                    }
                }
                return true; // Keep checking other models
            });
    }
    
    if (!this->teleport_requested)
    {
        return;
    }

    bool found_something_to_reset = false;

    // Loop through our memory bank of dynamic robots
    for (auto const& [robot_entity, original_pose] : this->initial_poses)
    {
        // Double-check the entity still exists in the world (wasn't deleted)
        if (_ecm.HasEntity(robot_entity))
        {
            found_something_to_reset = true;

            // 1. Teleport it back to its SPECIFIC memorized pose
            _ecm.SetComponentData<gz::sim::components::WorldPoseCmd>(robot_entity, original_pose);

            // 2. Reset all joints inside this specific robot
            _ecm.Each<gz::sim::components::Joint, gz::sim::components::ParentEntity>(
                [&](const gz::sim::Entity &_jointEntity,
                    const gz::sim::components::Joint *,
                    const gz::sim::components::ParentEntity *_parent) -> bool
                {
                    if (_parent->Data() == robot_entity)
                    {
                        _ecm.SetComponentData<gz::sim::components::JointPositionReset>(_jointEntity, {0.0});
                        _ecm.SetComponentData<gz::sim::components::JointVelocityReset>(_jointEntity, {0.0});
                    }
                    return true; 
                });
        }
    }

    if (found_something_to_reset) {
        gzerr << "[ResetSimPlugin] Successfully teleported dynamic agents!" << std::endl;
    } else {
        gzerr << "[ResetSimPlugin] Keystroke Reset Failed: No dynamic robots found!" << std::endl;
    }

    this->teleport_requested = false;
}

GZ_ADD_PLUGIN (
    reset_plugin::ResetSimPlugin,
    gz::sim::System,
    gz::sim::ISystemConfigure,
    gz::sim::ISystemPreUpdate
)