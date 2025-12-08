# Chapter 3: ROS 2 Fundamentals

## Learning Objectives

By the end of this chapter, you will be able to:
- Understand the architecture and design philosophy of ROS 2
- Create and manage nodes, topics, services, and actions
- Build ROS 2 packages with proper structure
- Write publishers and subscribers in Python and C++
- Use launch files to orchestrate complex robot systems
- Navigate the ROS 2 ecosystem and tools
- Understand Quality of Service (QoS) policies
- Debug and troubleshoot ROS 2 applications

---

## 3.1 What is ROS 2?

**Robot Operating System 2 (ROS 2)** is an open-source middleware framework for building robot applications. Despite its name, ROS 2 is not an operating system but rather a collection of software libraries and tools that provide:

- **Communication infrastructure**: Message passing between processes
- **Hardware abstraction**: Unified interfaces for sensors and actuators
- **Package management**: Modular, reusable components
- **Development tools**: Debugging, visualization, simulation
- **Community ecosystem**: Thousands of packages and active support

### 3.1.1 Why ROS 2 (vs. ROS 1)?

ROS 1 (released 2007) was revolutionary but had limitations. ROS 2 (released 2017) addresses these:

| Feature | ROS 1 | ROS 2 |
|---------|-------|-------|
| **Communication** | Custom TCP/UDP | DDS (industry standard) |
| **Real-time** | Limited support | Real-time capable |
| **Security** | None | Built-in encryption, authentication |
| **Multi-robot** | Difficult | Native support |
| **Cross-platform** | Linux-focused | Linux, Windows, macOS |
| **Lifecycle** | Simple start/stop | Managed lifecycle nodes |
| **QoS** | Best-effort only | Configurable policies |
| **Python** | Python 2 | Python 3 |

### 3.1.2 DDS: The Foundation

ROS 2 uses **Data Distribution Service (DDS)** as its middleware:

- **Decentralized**: No master node (unlike ROS 1)
- **Discoverable**: Nodes automatically find each other
- **Reliable**: Configurable message delivery guarantees
- **Scalable**: Efficient multi-robot communication
- **Industry-proven**: Used in defense, aerospace, automotive

Popular DDS implementations:
- **Fast DDS** (eProsima) - Default in ROS 2
- **Cyclone DDS** (Eclipse) - Lightweight alternative
- **Connext DDS** (RTI) - Commercial, high-performance

---

## 3.2 Core Concepts

### 3.2.1 Computational Graph

ROS 2 applications form a **computational graph** where:
- **Nodes** are vertices (processes)
- **Topics/Services/Actions** are edges (communication)

```
┌─────────┐  topic: /cmd_vel   ┌──────────┐
│ Planner ├──────────────────→ │  Robot   │
└─────────┘                     │ Controller│
                                └────┬─────┘
                                     │
                          topic: /odom
                                     ↓
                                ┌─────────┐
                                │Localizer│
                                └─────────┘
```

### 3.2.2 Nodes

A **node** is a single-purpose executable process:
- Performs one computational task (e.g., sensor driver, controller, planner)
- Communicates with other nodes via topics/services/actions
- Can be written in Python, C++, or other supported languages
- Runs independently, enabling modularity and fault isolation

**Design Principle**: Keep nodes focused. One node = one responsibility.

**Example Nodes**:
- `camera_driver`: Publishes camera images
- `object_detector`: Subscribes to images, publishes detected objects
- `motion_planner`: Plans trajectories to goal positions
- `motor_controller`: Sends commands to actuators

### 3.2.3 Topics (Publish-Subscribe)

**Topics** enable asynchronous, many-to-many communication:

- **Publisher**: Sends messages to a topic
- **Subscriber**: Receives messages from a topic
- **Message**: Typed data structure (e.g., sensor data, commands)

**Characteristics**:
- Asynchronous (fire-and-forget)
- One-to-many or many-to-many
- No acknowledgment
- Best for streaming data (sensor readings, commands)

**Example**:
```
Publisher (camera_driver)  →  topic: /image  →  Subscriber (object_detector)
                                               →  Subscriber (image_viewer)
```

### 3.2.4 Services (Request-Reply)

**Services** enable synchronous, one-to-one communication:

- **Client**: Sends request, waits for response
- **Server**: Processes request, returns response
- **Service**: Defined by request and response message types

**Characteristics**:
- Synchronous (blocking)
- One-to-one
- Acknowledged
- Best for infrequent, short-duration operations

**Example**:
```
Client (planner) → service: /compute_path → Server (path_planner)
                 ← returns path
```

### 3.2.5 Actions (Goal-Based)

**Actions** enable long-running, goal-oriented tasks with feedback:

- **Client**: Sends goal, receives feedback and result
- **Server**: Executes goal, provides periodic feedback, returns result
- **Action**: Defined by goal, feedback, and result message types

**Characteristics**:
- Asynchronous with feedback
- Can be canceled mid-execution
- Best for long-running tasks (navigation, manipulation)

**Example**:
```
Client (mission_planner)
    ↓ sends goal
Action Server (navigator)
    ↓ feedback: "50% to goal"
    ↓ feedback: "75% to goal"
    ↓ result: "Goal reached"
Client receives result
```

---

## 3.3 ROS 2 Package Structure

A **package** is the organizational unit in ROS 2, containing:
- Source code (Python or C++)
- Configuration files
- Launch files
- Message/service/action definitions
- Dependencies

### 3.3.1 Python Package Structure

```
my_robot_pkg/
├── package.xml          # Package metadata and dependencies
├── setup.py             # Python package setup
├── setup.cfg            # Install configuration
├── my_robot_pkg/        # Python module
│   ├── __init__.py
│   ├── my_node.py       # Node implementation
│   └── utils.py         # Helper functions
├── launch/              # Launch files
│   └── my_launch.py
├── config/              # Configuration files
│   └── params.yaml
└── resource/            # Resource marker
    └── my_robot_pkg
```

### 3.3.2 C++ Package Structure

```
my_robot_cpp_pkg/
├── package.xml          # Package metadata
├── CMakeLists.txt       # Build configuration
├── include/             # Header files
│   └── my_robot_cpp_pkg/
│       └── my_node.hpp
├── src/                 # Source files
│   └── my_node.cpp
├── launch/              # Launch files
│   └── my_launch.py
└── config/              # Configuration files
    └── params.yaml
```

### 3.3.3 Creating a Package

**Python Package**:
```bash
ros2 pkg create --build-type ament_python my_robot_pkg --dependencies rclpy std_msgs
```

**C++ Package**:
```bash
ros2 pkg create --build-type ament_cmake my_robot_cpp_pkg --dependencies rclcpp std_msgs
```

---

## 3.4 Writing Your First Node

### 3.4.1 Python Publisher

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        self.timer = self.create_timer(0.5, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.i}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.i += 1

def main(args=None):
    rclpy.init(args=args)
    node = MinimalPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**Key Elements**:
- `Node`: Base class for all ROS 2 nodes
- `create_publisher()`: Creates a publisher on a topic
- `create_timer()`: Periodic callback (0.5 seconds here)
- `publish()`: Sends message to topic
- `spin()`: Keeps node alive, processing callbacks

### 3.4.2 Python Subscriber

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalSubscriber(Node):
    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)
    node = MinimalSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### 3.4.3 C++ Publisher

```cpp
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

class MinimalPublisher : public rclcpp::Node {
public:
  MinimalPublisher() : Node("minimal_publisher"), count_(0) {
    publisher_ = this->create_publisher<std_msgs::msg::String>("topic", 10);
    timer_ = this->create_wall_timer(
      std::chrono::milliseconds(500),
      std::bind(&MinimalPublisher::timer_callback, this));
  }

private:
  void timer_callback() {
    auto message = std_msgs::msg::String();
    message.data = "Hello, world! " + std::to_string(count_++);
    RCLCPP_INFO(this->get_logger(), "Publishing: '%s'", message.data.c_str());
    publisher_->publish(message);
  }
  
  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
  size_t count_;
};

int main(int argc, char * argv[]) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MinimalPublisher>());
  rclcpp::shutdown();
  return 0;
}
```

---

## 3.5 Message Types

ROS 2 uses strongly-typed messages defined in `.msg` files.

### 3.5.1 Common Message Packages

**std_msgs**: Basic types
- `Bool`, `Int32`, `Float64`, `String`
- `Header` (timestamp + frame_id)

**geometry_msgs**: Spatial types
- `Point`, `Vector3`, `Quaternion`
- `Pose`, `PoseStamped`, `Transform`
- `Twist` (linear + angular velocity)

**sensor_msgs**: Sensor data
- `Image`, `CompressedImage`
- `LaserScan`, `PointCloud2`
- `Imu`, `NavSatFix` (GPS)
- `JointState`

**nav_msgs**: Navigation
- `Odometry` (robot pose + velocity)
- `Path` (sequence of poses)
- `OccupancyGrid` (2D map)

### 3.5.2 Custom Messages

Define custom messages in `msg/` directory:

**msg/Person.msg**:
```
string name
uint8 age
float32 height
```

Add to `package.xml`:
```xml
<depend>rosidl_default_generators</depend>
<exec_depend>rosidl_default_runtime</exec_depend>
```

Add to `CMakeLists.txt` (C++) or `setup.py` (Python).

**Usage**:
```python
from my_robot_pkg.msg import Person

msg = Person()
msg.name = "Alice"
msg.age = 30
msg.height = 1.65
```

---

## 3.6 Parameters

Parameters allow runtime configuration without code changes.

### 3.6.1 Declaring Parameters

```python
class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')
        
        # Declare parameter with default
        self.declare_parameter('max_speed', 1.0)
        self.declare_parameter('robot_name', 'robot1')
        
        # Get parameter values
        max_speed = self.get_parameter('max_speed').value
        robot_name = self.get_parameter('robot_name').value
        
        self.get_logger().info(f'Max speed: {max_speed}, Name: {robot_name}')
```

### 3.6.2 Setting Parameters

**From command line**:
```bash
ros2 run my_pkg my_node --ros-args -p max_speed:=2.0 -p robot_name:=robot2
```

**From YAML file** (`config/params.yaml`):
```yaml
my_node:
  ros__parameters:
    max_speed: 2.5
    robot_name: "robot3"
```

Load in launch file:
```python
Node(
    package='my_pkg',
    executable='my_node',
    parameters=['/path/to/params.yaml']
)
```

### 3.6.3 Dynamic Reconfiguration

Parameters can be changed at runtime:

```python
# In node
self.add_on_set_parameters_callback(self.parameter_callback)

def parameter_callback(self, params):
    for param in params:
        if param.name == 'max_speed':
            self.max_speed = param.value
            self.get_logger().info(f'Updated max_speed to {param.value}')
    return SetParametersResult(successful=True)
```

**Change from command line**:
```bash
ros2 param set /my_node max_speed 3.0
```

---

## 3.7 Launch Files

Launch files start multiple nodes with configurations.

### 3.7.1 Python Launch File

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='my_robot_pkg',
            executable='sensor_driver',
            name='camera',
            parameters=[{'frame_rate': 30}]
        ),
        Node(
            package='my_robot_pkg',
            executable='controller',
            name='robot_controller',
            output='screen',
            parameters=['/path/to/params.yaml']
        ),
        Node(
            package='my_robot_pkg',
            executable='visualizer',
            name='viz'
        )
    ])
```

**Launch**:
```bash
ros2 launch my_robot_pkg my_launch.py
```

### 3.7.2 Advanced Launch Features

**Include other launch files**:
```python
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

IncludeLaunchDescription(
    PythonLaunchDescriptionSource('/path/to/other_launch.py')
)
```

**Conditional launching**:
```python
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration

Node(
    package='my_pkg',
    executable='debug_node',
    condition=IfCondition(LaunchConfiguration('debug'))
)
```

**Arguments**:
```python
from launch.actions import DeclareLaunchArgument

DeclareLaunchArgument(
    'robot_name',
    default_value='robot1',
    description='Name of the robot'
)
```

---

## 3.8 Quality of Service (QoS)

QoS policies control message delivery behavior.

### 3.8.1 QoS Profiles

**Reliability**:
- `RELIABLE`: Guaranteed delivery (retries until acknowledged)
- `BEST_EFFORT`: Send once, no retries (lower latency)

**Durability**:
- `TRANSIENT_LOCAL`: Store last message for late joiners
- `VOLATILE`: No message storage

**History**:
- `KEEP_LAST(n)`: Keep only last n messages
- `KEEP_ALL`: Keep all messages (memory limited)

**Liveliness**:
- `AUTOMATIC`: Node is alive if process is running
- `MANUAL_BY_TOPIC`: Publisher must assert liveliness

### 3.8.2 Common QoS Profiles

```python
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

# Sensor data (best-effort, volatile)
qos_sensor = QoSProfile(
    depth=10,
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.VOLATILE
)

# System state (reliable, transient local)
qos_system = QoSProfile(
    depth=10,
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.TRANSIENT_LOCAL
)

# Create publisher with QoS
self.publisher_ = self.create_publisher(String, 'topic', qos_sensor)
```

### 3.8.3 Predefined QoS Profiles

```python
from rclpy.qos import qos_profile_sensor_data, qos_profile_system_default

# Sensor data profile (best-effort)
pub = self.create_publisher(Image, '/camera', qos_profile_sensor_data)

# Default profile (reliable)
pub = self.create_publisher(String, '/status', qos_profile_system_default)
```

---

## 3.9 Essential ROS 2 Tools

### 3.9.1 Command-Line Tools

**Node management**:
```bash
ros2 node list                    # List running nodes
ros2 node info /my_node           # Node details
```

**Topic inspection**:
```bash
ros2 topic list                   # List topics
ros2 topic echo /my_topic         # Print messages
ros2 topic info /my_topic         # Topic details
ros2 topic hz /my_topic           # Message rate
ros2 topic pub /cmd_vel ...       # Publish manually
```

**Service calls**:
```bash
ros2 service list                 # List services
ros2 service call /my_service ... # Call service
```

**Parameter management**:
```bash
ros2 param list                   # List parameters
ros2 param get /my_node my_param  # Get parameter
ros2 param set /my_node my_param value  # Set parameter
```

**Bag files** (recording/playback):
```bash
ros2 bag record -a                # Record all topics
ros2 bag record /topic1 /topic2   # Record specific topics
ros2 bag play my_bag.db3          # Playback recording
ros2 bag info my_bag.db3          # Bag file info
```

### 3.9.2 Visualization Tools

**RViz2**: 3D visualization
```bash
ros2 run rviz2 rviz2
```
- Visualize robot models (URDF)
- Sensor data (camera, LIDAR, point clouds)
- TF transforms
- Path planning

**rqt**: Qt-based GUI tools
```bash
rqt                               # Main rqt window
rqt_graph                         # Node/topic graph
rqt_plot                          # Plot numeric data
rqt_console                       # Log messages
rqt_reconfigure                   # Dynamic reconfigure
```

### 3.9.3 Debugging Tools

**ros2 doctor**: System health check
```bash
ros2 doctor                       # Check ROS 2 setup
ros2 doctor --report              # Detailed report
```

**Logging levels**:
```bash
ros2 run my_pkg my_node --ros-args --log-level DEBUG
```

Levels: DEBUG, INFO, WARN, ERROR, FATAL

---

## 3.10 TF2: Coordinate Transforms

**TF2** manages coordinate frame transformations between different parts of the robot.

### 3.10.1 Frame Tree

```
        map
         │
    ┌────┴────┐
   odom      camera_link
    │
base_link
    │
  ┌─┴─┐
left_wheel  right_wheel
```

### 3.10.2 Broadcasting Transforms

```python
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped

class TFPublisher(Node):
    def __init__(self):
        super().__init__('tf_publisher')
        self.br = TransformBroadcaster(self)
        self.timer = self.create_timer(0.1, self.broadcast_transform)

    def broadcast_transform(self):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'base_link'
        t.child_frame_id = 'camera_link'
        
        # Set translation
        t.transform.translation.x = 0.5
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.3
        
        # Set rotation (quaternion)
        t.transform.rotation.w = 1.0
        
        self.br.sendTransform(t)
```

### 3.10.3 Listening to Transforms

```python
from tf2_ros import TransformListener, Buffer

class TFListener(Node):
    def __init__(self):
        super().__init__('tf_listener')
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.timer = self.create_timer(1.0, self.lookup_transform)

    def lookup_transform(self):
        try:
            trans = self.tf_buffer.lookup_transform(
                'base_link',
                'camera_link',
                rclpy.time.Time())
            self.get_logger().info(f'Transform: {trans}')
        except Exception as e:
            self.get_logger().warn(f'Could not transform: {e}')
```

---

## 3.11 Building and Running

### 3.11.1 Build Workspace

```bash
# Create workspace
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

# Create packages
ros2 pkg create my_robot_pkg --build-type ament_python

# Build
cd ~/ros2_ws
colcon build

# Source workspace
source install/setup.bash
```

### 3.11.2 Build Options

```bash
# Build specific packages
colcon build --packages-select my_robot_pkg

# Build with debug symbols
colcon build --cmake-args -DCMAKE_BUILD_TYPE=Debug

# Symlink install (Python packages, no rebuild needed)
colcon build --symlink-install
```

### 3.11.3 Running Nodes

```bash
# Run single node
ros2 run my_robot_pkg my_node

# Run with arguments
ros2 run my_robot_pkg my_node --ros-args -p param:=value

# Run launch file
ros2 launch my_robot_pkg my_launch.py
```

---

## 3.12 Best Practices

### 3.12.1 Node Design

✅ **Single Responsibility**: One node, one task  
✅ **Reusability**: Write generic, configurable nodes  
✅ **Error Handling**: Graceful failure and recovery  
✅ **Logging**: Use appropriate log levels  
✅ **Resource Management**: Clean up in destructors  

### 3.12.2 Communication Patterns

✅ **Topics**: For streaming data (sensor readings, commands)  
✅ **Services**: For infrequent, short operations (configuration, queries)  
✅ **Actions**: For long-running goals (navigation, manipulation)  
✅ **Parameters**: For configuration, not data flow  

### 3.12.3 Performance

✅ **QoS**: Match QoS to use case (best-effort for sensors)  
✅ **Message Size**: Keep messages compact  
✅ **Frequency**: Don't publish faster than needed  
✅ **Zero-Copy**: Use intra-process communication for large data  

### 3.12.4 Code Organization

✅ **Packages**: Group related functionality  
✅ **Namespaces**: Avoid topic/node name collisions  
✅ **Launch Files**: Parameterize for flexibility  
✅ **Documentation**: README, inline comments, API docs  

---

## 3.13 Chapter Summary

ROS 2 is a middleware framework built on DDS that provides communication infrastructure, hardware abstraction, and development tools for robotics. It addresses ROS 1 limitations with real-time support, security, multi-robot capabilities, and configurable QoS.

Core concepts include nodes (single-purpose processes), topics (pub-sub communication), services (request-reply), and actions (goal-based with feedback). Packages organize code, configuration, and launch files using ament build system.

Message types are strongly typed and defined in standard packages like std_msgs, geometry_msgs, sensor_msgs, and nav_msgs. Custom messages can be defined for application-specific data. Parameters enable runtime configuration without code changes.

Launch files orchestrate multiple nodes with configurations, supporting includes, conditions, and arguments. QoS policies control message delivery with profiles for reliability, durability, history, and liveliness.

Essential tools include command-line utilities for node/topic/service/parameter inspection, bag files for recording/playback, RViz2 for 3D visualization, and rqt for GUI-based tools. TF2 manages coordinate transformations between robot frames.

Best practices emphasize single-responsibility nodes, appropriate communication patterns, performance optimization through QoS, and clean code organization with proper documentation.

---

## Key Takeaways

✅ ROS 2 uses DDS for decentralized, real-time, secure communication  
✅ Nodes communicate via topics (pub-sub), services (req-reply), actions (goals)  
✅ Packages organize code with ament_python or ament_cmake build types  
✅ Messages are strongly typed; use standard packages or define custom types  
✅ Parameters enable runtime configuration; declare and access in nodes  
✅ Launch files orchestrate multi-node systems with configurations  
✅ QoS policies control reliability, durability, history for different use cases  
✅ Essential tools: ros2 CLI, bag files, RViz2, rqt, TF2 transforms  
✅ Best practices: single responsibility, appropriate patterns, QoS tuning  

---

## Further Reading

- **Official Documentation**:
  - ROS 2 Documentation (docs.ros.org)
  - ROS 2 Design (design.ros2.org)
  - DDS Specification (omg.org)

- **Books**:
  - "A Concise Introduction to Robot Programming with ROS 2" by Francisco Martín Rico
  - "ROS 2 Robotics Developer Guide" (Packt)

- **Tutorials**:
  - Official ROS 2 Tutorials (docs.ros.org/en/humble/Tutorials.html)
  - The Construct ROS 2 Courses
  - ROS 2 YouTube Channel

- **Community**:
  - ROS Discourse (discourse.ros.org)
  - ROS Answers (answers.ros.org)
  - GitHub ROS 2 Repositories

---

**Next Chapter**: Digital Twin Simulation (Gazebo + Isaac) – We'll learn to create virtual environments for testing and training robots before real-world deployment.