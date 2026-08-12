import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_dir = get_package_share_directory("unitree_ros")

    default_param_file = os.path.join(pkg_dir, "config", "params.yaml")

    params_file_arg = DeclareLaunchArgument(
        "params_file",
        default_value=default_param_file,
        description="Parameters file to be used.",
    )

    wifi_arg = DeclareLaunchArgument(
        "wifi",
        default_value="false",
        description="Use the WiFi IP for communicating with the robot.",
    )

    namespace_arg = DeclareLaunchArgument(
        "namespace",
        default_value="unitree",
        description="Namespace for Unitree ROS topics.",
    )

    cmd_vel_topic_arg = DeclareLaunchArgument(
        "cmd_vel_topic",
        default_value="cmd_vel",
        description="Topic from which the Unitree driver receives velocity commands.",
    )

    low_batt_threshold_arg = DeclareLaunchArgument(
        "low_batt_threshold",
        default_value="0",
        description="Low battery shutdown threshold.",
    )

    use_unitree_tf_arg = DeclareLaunchArgument(
        "use_unitree_tf",
        default_value="false",
        description=(
            "If true, publish Unitree TF on /tf. "
            "If false, isolate Unitree TF under the Unitree namespace."
        ),
    )

    return LaunchDescription(
        [
            params_file_arg,
            wifi_arg,
            namespace_arg,
            cmd_vel_topic_arg,
            low_batt_threshold_arg,
            use_unitree_tf_arg,
            OpaqueFunction(function=launch_unitree_driver),
        ]
    )


def launch_unitree_driver(context):
    params_file = LaunchConfiguration("params_file").perform(context)

    wifi = LaunchConfiguration("wifi").perform(context)
    namespace = LaunchConfiguration("namespace").perform(context)
    cmd_vel_topic = LaunchConfiguration("cmd_vel_topic").perform(context)

    low_batt_threshold = int(LaunchConfiguration("low_batt_threshold").perform(context))

    use_unitree_tf = (
        LaunchConfiguration("use_unitree_tf").perform(context).lower() == "true"
    )

    if wifi == "true":
        robot_ip = "192.168.12.1"
    else:
        robot_ip = "192.168.123.161"

    remappings = [
        # The driver subscribes to cmd_vel_topic_name.
        # Make that resolve to the requested external topic.
        ("cmd_vel", cmd_vel_topic),
    ]

    if use_unitree_tf:
        # Unitree TF goes into the normal global TF tree.
        remappings.append(("/tf", "/tf"))
        remappings.append(("/tf_static", "/tf_static"))
    else:
        # Isolate Unitree TF from the user's main TF tree.
        remappings.append(("/tf", f"/{namespace}/tf"))
        remappings.append(("/tf_static", f"/{namespace}/tf_static"))

    return [
        Node(
            package="unitree_ros",
            executable="unitree_driver",
            namespace=namespace,
            parameters=[
                params_file,
                {
                    "robot_ip": robot_ip,
                    "low_batt_shutdown_threshold": low_batt_threshold,
                    "cmd_vel_topic_name": cmd_vel_topic,
                },
            ],
            remappings=remappings,
            output="screen",
        )
    ]
