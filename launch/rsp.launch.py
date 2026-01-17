import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node

import xacro


def generate_launch_description():
    # Launch args
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_jsp_gui = LaunchConfiguration('use_jsp_gui')

    # Paths
    pkg_share = get_package_share_directory('autonomous')
    xacro_file = os.path.join(pkg_share, 'description', 'robot.urdf.xacro')

    # Process xacro -> URDF
    robot_description_config = xacro.process_file(xacro_file)
    robot_description = robot_description_config.toxml()

    # Nodes
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        condition=None,  # kept simple; see GUI node below
    )

    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        condition=None,  # kept simple; see note below
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': use_sim_time
        }],
    )

    # NOTE about GUI switching:
    # Launch "use_jsp_gui:=true" to use the GUI.
    # Easiest robust approach: we use one or the other via IfCondition.
    # (see version below with proper conditions)

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation (Gazebo) clock if true'
        ),
        DeclareLaunchArgument(
            'use_jsp_gui',
            default_value='false',
            description='Use joint_state_publisher_gui if true'
        ),

        # --- Proper conditional selection (recommended) ---
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
            condition=__import__('launch.conditions').conditions.UnlessCondition(use_jsp_gui),
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
            condition=__import__('launch.conditions').conditions.IfCondition(use_jsp_gui),
        ),

        robot_state_publisher,
    ])
