cmake_minimum_required(VERSION 3.10)
project(unitree_ros)

# Default to C99
if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()


find_package(rosidl_default_generators REQUIRED)
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)


# --------------------------------
# -       Setters Section        -
# --------------------------------

if("${CMAKE_SYSTEM_PROCESSOR}" MATCHES "x86_64.*")
  SET(ARCH amd64)
else()
  SET(ARCH arm64)
endif()

SET(EXTRA_LIBS 
    -pthread 
    libunitree_legged_sdk.a 
    libfaceLight_SDK_${ARCH}.so
)

SET(SOURCES 
    src/unitree_ros.cpp 
    src/unitree_driver.cpp 
    src/serializers.cpp
)

SET(DEPENDENCIES rclcpp std_msgs nav_msgs sensor_msgs geometry_msgs tf2 tf2_ros)

# --------------------------------
# -      Libraries Section       -
# --------------------------------

link_directories(${CMAKE_SOURCE_DIR}/utils/unitree_legged_sdk/lib/cpp/${ARCH})
link_directories(${CMAKE_SOURCE_DIR}/utils/faceLightSDK_Nano/lib)


include_directories(include 
                   ${CMAKE_SOURCE_DIR}/utils/unitree_legged_sdk/include)
include_directories(include 
                   ${CMAKE_SOURCE_DIR}/utils/faceLightSDK_Nano/include)

# --------------------------------
# - Message Generatation Section -
# --------------------------------
              
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/BmsState.msg"
  "msg/SensorRanges.msg"
  DEPENDENCIES builtin_interfaces std_msgs geometry_msgs sensor_msgs nav_msgs
)


# -----------------------
# -    Build Section    -
# -----------------------

# NOTE This part is incompatible with newer ROS2 versions (e.g., kilted)
# add_executable(unitree_driver src/unitree_ros_node.cpp ${SOURCES})
# ament_target_dependencies(unitree_driver ${DEPENDENCIES})
# rosidl_get_typesupport_target(cpp_typesupport_target
#   ${PROJECT_NAME} rosidl_typesupport_cpp)
# target_link_libraries(unitree_driver "${cpp_typesupport_target}" ${EXTRA_LIBS})

# NOTE This part makes the package build with newer ROS2 versions
add_executable(unitree_driver
  src/unitree_ros_node.cpp
  ${SOURCES}
)

rosidl_get_typesupport_target(
  cpp_typesupport_target
  ${PROJECT_NAME}
  rosidl_typesupport_cpp
)

target_link_libraries(unitree_driver PUBLIC
  "${cpp_typesupport_target}"

  rclcpp::rclcpp
  tf2::tf2
  tf2_ros::tf2_ros

  ${geometry_msgs_TARGETS}
  ${nav_msgs_TARGETS}
  ${sensor_msgs_TARGETS}
  ${std_msgs_TARGETS}

  ${EXTRA_LIBS}
)



# -------------------
# - Install Section -
# -------------------

install(
  DIRECTORY include ${CMAKE_SOURCE_DIR}/utils/unitree_legged_sdk/include ${CMAKE_SOURCE_DIR}/utils/faceLightSDK_Nano/include
  DESTINATION include
)

install(
  DIRECTORY config launch
  DESTINATION share/${PROJECT_NAME}
)

install(TARGETS 
  unitree_driver
  DESTINATION lib/${PROJECT_NAME}
  INCLUDES DESTINATION include
)

install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/utils/faceLightSDK_Nano/lib/libfaceLight_SDK_${ARCH}.so
        DESTINATION lib)

ament_package()
