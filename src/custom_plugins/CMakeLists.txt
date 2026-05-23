cmake_minimum_required(VERSION 3.8)
project(custom_plugins)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclpp REQUIRED)
find_package(std-srvs REQUIRED)
find_package(gz-cmake3 REQUIRED)
find_package(std-msgs REQUIRED)

add_library(${PROJECT_NAME} SHARED
  src/sim_reset_plugin.cpp
)

ament_target_dependencies(${PROJECT_NAME}
  rclcpp
  std_srvs
  std_msgs
)

target_link_libraries(${PROJECT_NAME}
  gz-sim8::gz-sim8
  gz-plugin2::gz-plugin2
  gz-transport13::gz-transport13
  gz-msgs10::gz-msgs10
)

install(TARGETS ${PROJECT_NAME}
  DIRECTORY src
  DESTINATION lib
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
