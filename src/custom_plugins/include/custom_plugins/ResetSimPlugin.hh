#pragma once

#include <gz/sim/System.hh> 
#include <gz/sim/Entity.hh>
#include <gz/sim/EntityComponentManager.hh>

namespace reset_plugin
{

class ResetSimPlugin :
    public gz::sim::System,
    public gz::sim::ISystemReset
    {   
        public:
            // Constructor
            ResetSimPlugin() = default;

            // ISystemReset reset method
            void Reset(const gz::sim::UpdateInfo &_info, gz::sim::EntityComponentManager &_ecm) override;
    };
}
