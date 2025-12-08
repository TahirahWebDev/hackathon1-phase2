# Chapter 6: Capstone - Simple AI-Robot Pipeline

## Learning Objectives

By the end of this chapter, you will be able to:
- Design an end-to-end AI-robot system architecture
- Integrate perception, reasoning, and control components
- Build a complete manipulation pipeline using learned concepts
- Deploy and test the system in simulation
- Troubleshoot common integration issues
- Plan for real-world deployment
- Understand best practices for production robotics systems

---

## 6.1 Project Overview

We'll build a **voice-controlled manipulation system** that demonstrates the full Physical AI stack:

**System**: Robot arm that follows natural language commands to manipulate objects

**Components**:
1. **Vision**: Camera for object detection
2. **Language**: Voice command processing
3. **Reasoning**: VLA model for task understanding
4. **Planning**: Motion planning for arm movement
5. **Control**: Joint control for execution
6. **Simulation**: Gazebo environment for testing

**Example Task**: "Pick up the red block and place it in the blue bin"

---

## 6.2 System Architecture

### 6.2.1 Overall Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                       │
│              (Voice Command / GUI)                      │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│              Language Processing Node                   │
│         (Speech-to-Text, Command Parsing)               │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│                  Vision Node                            │
│    (Object Detection, Pose Estimation)                  │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│                   VLA Node                              │
│     (Task Understanding, Action Planning)               │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│              Motion Planning Node                       │
│         (MoveIt, Trajectory Generation)                 │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│              Robot Control Node                         │
│         (Joint Commands, Gripper Control)               │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│            Gazebo Simulation / Real Robot               │
└─────────────────────────────────────────────────────────┘
```

### 6.2.2 ROS 2 Topic Flow

```
/voice_command (std_msgs/String)
     ↓
/parsed_command (custom_msgs/TaskCommand)
     ↓
/camera/image (sensor_msgs/Image)
/camera/depth (sensor_msgs/Image)
     ↓
/detected_objects (vision_msgs/Detection3DArray)
     ↓
/target_pose (geometry_msgs/PoseStamped)
     ↓
/joint_trajectory (trajectory_msgs/JointTrajectory)
     ↓
/joint_commands (sensor_msgs/JointState)
```

---

## 6.3 Component Implementation

### 6.3.1 Robot Setup (URDF + Gazebo)

**robot_description.urdf.xacro**:
```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="manipulator">
  
  <!-- Properties -->
  <xacro:property name="link_length" value="0.3"/>
  <xacro:property name="link_radius" value="0.05"/>
  
  <!-- Base Link -->
  <link name="base_link">
    <visual>
      <geometry>
        <cylinder radius="0.1" length="0.1"/>
      </geometry>
      <material name="grey">
        <color rgba="0.5 0.5 0.5 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.1" length="0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="5.0"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.1"/>
    </inertial>
  </link>
  
  <!-- Shoulder Joint -->
  <joint name="shoulder_pan_joint" type="revolute">
    <parent link="base_link"/>
    <child link="shoulder_link"/>
    <origin xyz="0 0 0.05" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-3.14" upper="3.14" effort="10" velocity="2.0"/>
  </joint>
  
  <link name="shoulder_link">
    <visual>
      <geometry>
        <cylinder radius="${link_radius}" length="${link_length}"/>
      </geometry>
      <origin xyz="0 0 ${link_length/2}" rpy="0 0 0"/>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="${link_radius}" length="${link_length}"/>
      </geometry>
      <origin xyz="0 0 ${link_length/2}" rpy="0 0 0"/>
    </collision>
    <inertial>
      <mass value="2.0"/>
      <origin xyz="0 0 ${link_length/2}" rpy="0 0 0"/>
      <inertia ixx="0.05" ixy="0" ixz="0" iyy="0.05" iyz="0" izz="0.01"/>
    </inertial>
  </link>
  
  <!-- Camera -->
  <link name="camera_link">
    <visual>
      <geometry>
        <box size="0.05 0.05 0.03"/>
      </geometry>
    </visual>
  </link>
  
  <joint name="camera_joint" type="fixed">
    <parent link="base_link"/>
    <child link="camera_link"/>
    <origin xyz="0.5 0 0.5" rpy="0 0.5 0"/>
  </joint>
  
  <!-- Gazebo: Camera Sensor -->
  <gazebo reference="camera_link">
    <sensor name="camera" type="camera">
      <camera>
        <horizontal_fov>1.047</horizontal_fov>
        <image>
          <width>640</width>
          <height>480</height>
        </image>
        <clip>
          <near>0.1</near>
          <far>100</far>
        </clip>
      </camera>
      <always_on>1</always_on>
      <update_rate>30</update_rate>
      <topic>camera/image</topic>
    </sensor>
  </gazebo>
  
  <!-- Add more joints and links for elbow, wrist, gripper -->
  
</robot>
```

### 6.3.2 Vision Node (Object Detection)

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection3DArray, Detection3D, ObjectHypothesisWithPose
from cv_bridge import CvBridge
import cv2
import numpy as np
import torch
from torchvision.models.detection import fasterrcnn_resnet50_fpn

class VisionNode(Node):
    def __init__(self):
        super().__init__('vision_node')
        
        # Load object detection model
        self.model = fasterrcnn_resnet50_fpn(pretrained=True)
        self.model.eval()
        
        # COCO class names
        self.class_names = ['background', 'person', 'bicycle', 'car', 'motorcycle',
                           'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
                           # ... (simplified, use full COCO classes in practice)
                           'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple']
        
        self.bridge = CvBridge()
        
        # Subscribers
        self.image_sub = self.create_subscription(
            Image, '/camera/image', self.image_callback, 10)
        self.depth_sub = self.create_subscription(
            Image, '/camera/depth', self.depth_callback, 10)
        
        # Publisher
        self.detection_pub = self.create_publisher(
            Detection3DArray, '/detected_objects', 10)
        
        self.latest_depth = None
        self.get_logger().info('Vision node initialized')
    
    def depth_callback(self, msg):
        self.latest_depth = self.bridge.imgmsg_to_cv2(msg, desired_encoding='32FC1')
    
    def image_callback(self, msg):
        # Convert to OpenCV format
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')
        
        # Detect objects
        detections = self.detect_objects(cv_image)
        
        # Publish detections
        self.detection_pub.publish(detections)
        
        # Visualize (optional)
        self.visualize_detections(cv_image, detections)
    
    def detect_objects(self, image):
        # Prepare image
        img_tensor = torch.from_numpy(image).permute(2, 0, 1).float() / 255.0
        img_tensor = img_tensor.unsqueeze(0)
        
        # Run detection
        with torch.no_grad():
            predictions = self.model(img_tensor)[0]
        
        # Convert to ROS message
        detection_array = Detection3DArray()
        detection_array.header.stamp = self.get_clock().now().to_msg()
        detection_array.header.frame_id = 'camera_link'
        
        # Filter by confidence
        for i, score in enumerate(predictions['scores']):
            if score > 0.7:  # Confidence threshold
                detection = Detection3D()
                
                # Class and confidence
                class_id = predictions['labels'][i].item()
                detection.results.append(ObjectHypothesisWithPose())
                detection.results[0].hypothesis.class_id = str(class_id)
                detection.results[0].hypothesis.score = score.item()
                
                # Bounding box
                box = predictions['boxes'][i].numpy()
                x_center = int((box[0] + box[2]) / 2)
                y_center = int((box[1] + box[3]) / 2)
                
                # Estimate 3D position using depth
                if self.latest_depth is not None:
                    depth = self.latest_depth[y_center, x_center]
                    
                    # Camera intrinsics (example values)
                    fx, fy = 525.0, 525.0
                    cx, cy = 320.0, 240.0
                    
                    # Back-project to 3D
                    x = (x_center - cx) * depth / fx
                    y = (y_center - cy) * depth / fy
                    z = depth
                    
                    detection.bbox.center.position.x = x
                    detection.bbox.center.position.y = y
                    detection.bbox.center.position.z = z
                
                detection_array.detections.append(detection)
        
        return detection_array
    
    def visualize_detections(self, image, detections):
        for det in detections.detections:
            class_id = int(det.results[0].hypothesis.class_id)
            class_name = self.class_names[class_id] if class_id < len(self.class_names) else 'unknown'
            score = det.results[0].hypothesis.score
            
            # Draw on image
            cv2.putText(image, f'{class_name}: {score:.2f}', 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow('Detections', image)
        cv2.waitKey(1)

def main():
    rclpy.init()
    node = VisionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

### 6.3.3 Task Planning Node (VLA)

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
from vision_msgs.msg import Detection3DArray
import torch
from transformers import CLIPProcessor, CLIPModel

class TaskPlanningNode(Node):
    def __init__(self):
        super().__init__('task_planning_node')
        
        # Load VLA model (simplified)
        self.clip = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        
        # Subscribers
        self.command_sub = self.create_subscription(
            String, '/voice_command', self.command_callback, 10)
        self.detection_sub = self.create_subscription(
            Detection3DArray, '/detected_objects', self.detection_callback, 10)
        
        # Publisher
        self.target_pub = self.create_publisher(
            PoseStamped, '/target_pose', 10)
        
        self.latest_detections = None
        self.get_logger().info('Task planning node initialized')
    
    def detection_callback(self, msg):
        self.latest_detections = msg
    
    def command_callback(self, msg):
        command = msg.data
        self.get_logger().info(f'Received command: {command}')
        
        # Parse command and find target object
        target_object = self.parse_command(command)
        
        # Find object in detections
        if self.latest_detections:
            target_pose = self.find_object(target_object)
            if target_pose:
                self.target_pub.publish(target_pose)
                self.get_logger().info(f'Published target pose for {target_object}')
            else:
                self.get_logger().warn(f'Object {target_object} not found')
    
    def parse_command(self, command):
        # Simple keyword extraction (in practice, use NLP)
        keywords = ['red', 'blue', 'green', 'cup', 'block', 'ball']
        for keyword in keywords:
            if keyword in command.lower():
                return keyword
        return None
    
    def find_object(self, target_name):
        # Find object matching target_name in detections
        # In practice, use CLIP for semantic matching
        
        for detection in self.latest_detections.detections:
            # Simplified: match based on class name
            # In real system, use CLIP embeddings
            
            pose_msg = PoseStamped()
            pose_msg.header.stamp = self.get_clock().now().to_msg()
            pose_msg.header.frame_id = 'base_link'
            pose_msg.pose.position = detection.bbox.center.position
            pose_msg.pose.orientation.w = 1.0
            
            return pose_msg
        
        return None

def main():
    rclpy.init()
    node = TaskPlanningNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

### 6.3.4 Motion Planning Node (MoveIt)

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from moveit_msgs.msg import DisplayTrajectory
from trajectory_msgs.msg import JointTrajectory
import moveit_commander

class MotionPlanningNode(Node):
    def __init__(self):
        super().__init__('motion_planning_node')
        
        # Initialize MoveIt
        moveit_commander.roscpp_initialize([])
        self.robot = moveit_commander.RobotCommander()
        self.scene = moveit_commander.PlanningSceneInterface()
        self.group = moveit_commander.MoveGroupCommander("arm")
        
        # Subscriber
        self.target_sub = self.create_subscription(
            PoseStamped, '/target_pose', self.target_callback, 10)
        
        # Publisher
        self.trajectory_pub = self.create_publisher(
            JointTrajectory, '/joint_trajectory', 10)
        
        self.get_logger().info('Motion planning node initialized')
    
    def target_callback(self, msg):
        self.get_logger().info('Planning motion to target')
        
        # Set target pose
        self.group.set_pose_target(msg.pose)
        
        # Plan trajectory
        plan = self.group.plan()
        
        if plan[0]:  # Plan successful
            # Execute trajectory (in simulation or real robot)
            self.group.execute(plan[1], wait=True)
            self.get_logger().info('Motion executed successfully')
        else:
            self.get_logger().error('Motion planning failed')

def main():
    rclpy.init()
    node = MotionPlanningNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

---

## 6.4 Integration & Launch

### 6.4.1 Complete Launch File

```python
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Paths
    pkg_gazebo = get_package_share_directory('capstone_gazebo')
    pkg_description = get_package_share_directory('capstone_description')
    
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world_file = os.path.join(pkg_gazebo, 'worlds', 'manipulation.world')
    urdf_file = os.path.join(pkg_description, 'urdf', 'robot.urdf.xacro')
    
    # Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ros_gz_sim'),
                        'launch', 'gz_sim.launch.py')
        ]),
        launch_arguments={'gz_args': f'-r {world_file}'}.items()
    )
    
    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': open(urdf_file).read(),
            'use_sim_time': use_sim_time
        }]
    )
    
    # Spawn robot
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'manipulator',
            '-topic', '/robot_description',
            '-x', '0', '-y', '0', '-z', '0.1'
        ]
    )
    
    # Vision node
    vision_node = Node(
        package='capstone_vision',
        executable='vision_node',
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )
    
    # Task planning node
    task_planning_node = Node(
        package='capstone_planning',
        executable='task_planning_node',
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )
    
    # Motion planning node
    motion_planning_node = Node(
        package='capstone_planning',
        executable='motion_planning_node',
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )
    
    # RViz
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(pkg_description, 'config', 'view.rviz')],
        parameters=[{'use_sim_time': use_sim_time}]
    )
    
    # ROS-Gazebo bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/camera/image@sensor_msgs/msg/Image@gz.msgs.Image',
            '/camera/depth@sensor_msgs/msg/Image@gz.msgs.Image',
            '/joint_states@sensor_msgs/msg/JointState@gz.msgs.Model'
        ],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )
    
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        gazebo,
        robot_state_publisher,
        spawn_robot,
        vision_node,
        task_planning_node,
        motion_planning_node,
        bridge,
        rviz
    ])
```

### 6.4.2 Running the System

```bash
# Terminal 1: Build workspace
cd ~/capstone_ws
colcon build --symlink-install
source install/setup.bash

# Terminal 2: Launch complete system
ros2 launch capstone_bringup system.launch.py

# Terminal 3: Send voice command
ros2 topic pub /voice_command std_msgs/msg/String "data: 'pick up the red block'"

# Terminal 4: Monitor system
ros2 topic echo /detected_objects
ros2 topic echo /target_pose
ros2 topic echo /joint_trajectory
```

---

## 6.5 Testing & Validation

### 6.5.1 Unit Tests

```python
import unittest
from capstone_vision.vision_node import VisionNode
import numpy as np

class TestVisionNode(unittest.TestCase):
    def setUp(self):
        self.node = VisionNode()
    
    def test_object_detection(self):
        # Create test image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Run detection
        detections = self.node.detect_objects(test_image)
        
        # Assertions
        self.assertIsNotNone(detections)
        self.assertIsInstance(detections.detections, list)
    
    def test_depth_estimation(self):
        # Test 3D pose estimation with depth
        depth_map = np.ones((480, 640), dtype=np.float32) * 1.0
        self.node.latest_depth = depth_map
        
        # Verify pose calculation
        # ... add specific tests

if __name__ == '__main__':
    unittest.main()
```

### 6.5.2 Integration Tests

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
import time

class IntegrationTest(Node):
    def __init__(self):
        super().__init__('integration_test')
        
        self.command_pub = self.create_publisher(String, '/voice_command', 10)
        self.pose_sub = self.create_subscription(
            PoseStamped, '/target_pose', self.pose_callback, 10)
        
        self.received_pose = False
    
    def pose_callback(self, msg):
        self.received_pose = True
        self.get_logger().info('Received target pose')
    
    def test_end_to_end(self):
        # Send command
        cmd = String()
        cmd.data = "pick up the red block"
        self.command_pub.publish(cmd)
        
        # Wait for response
        start_time = time.time()
        while not self.received_pose and (time.time() - start_time) < 5.0:
            rclpy.spin_once(self, timeout_sec=0.1)
        
        assert self.received_pose, "Failed to receive target pose"
        self.get_logger().info('Integration test passed')

def main():
    rclpy.init()
    test = IntegrationTest()
    test.test_end_to_end()
    test.destroy_node()
    rclpy.shutdown()
```

---

## 6.6 Troubleshooting Guide

### 6.6.1 Common Issues

**Issue 1: Robot not visible in Gazebo**
- **Cause**: URDF parsing error or spawn failure
- **Solution**:
  ```bash
  # Check URDF validity
  check_urdf robot.urdf
  
  # Verify spawn arguments
  ros2 run ros_gz_sim create --help
  ```

**Issue 2: Camera not publishing images**
- **Cause**: Missing Gazebo sensor plugin or bridge
- **Solution**:
  ```bash
  # Check Gazebo topics
  gz topic -l
  
  # Verify bridge configuration
  ros2 run ros_gz_bridge parameter_bridge --help
  ```

**Issue 3: Object detection not working**
- **Cause**: Model not loaded or incorrect input format
- **Solution**:
  ```python
  # Add logging
  self.get_logger().info(f'Image shape: {image.shape}')
  self.get_logger().info(f'Detections: {len(predictions["scores"])}')
  ```

**Issue 4: Motion planning fails**
- **Cause**: Unreachable target or collision
- **Solution**:
  ```python
  # Visualize planning scene
  self.scene.get_known_object_names()
  
  # Check joint limits
  self.group.get_current_joint_values()
  ```

### 6.6.2 Debugging Tools

**ROS 2 Tools**:
```bash
# Node graph
rqt_graph

# Topic monitoring
ros2 topic hz /camera/image
ros2 topic bw /camera/image

# TF tree
ros2 run tf2_tools view_frames

# Log analysis
ros2 run rqt_console rqt_console
```

**Performance Profiling**:
```bash
# CPU/Memory usage
ros2 run resource_usage resource_usage

# Latency measurement
ros2 topic delay /camera/image
```

---

## 6.7 Real-World Deployment

### 6.7.1 Hardware Checklist

**Compute**:
- [ ] Jetson Orin or equivalent (GPU for VLA inference)
- [ ] Minimum 8GB RAM
- [ ] 128GB SSD storage

**Sensors**:
- [ ] RGB-D camera (Intel RealSense D435)
- [ ] Optional: LIDAR for collision avoidance

**Robot**:
- [ ] 6-7 DOF manipulator arm
- [ ] Gripper with force feedback
- [ ] Emergency stop button

**Networking**:
- [ ] Ethernet connection (lowest latency)
- [ ] WiFi fallback for monitoring

### 6.7.2 Sim-to-Real Checklist

- [ ] **Calibrate camera**: Intrinsic and extrinsic parameters
- [ ] **Measure robot**: Joint limits, max velocities, payload capacity
- [ ] **Test sensors**: Verify noise characteristics match simulation
- [ ] **Tune controllers**: PID gains for real actuators
- [ ] **Safety limits**: Joint position/velocity limits, workspace bounds
- [ ] **Collision avoidance**: Add safety margin for planning
- [ ] **Gradual testing**: Start with simple motions, increase complexity

### 6.7.3 Production Deployment

```python
class ProductionNode(Node):
    def __init__(self):
        super().__init__('production_node')
        
        # Health monitoring
        self.create_timer(1.0, self.health_check)
        self.error_count = 0
        self.max_errors = 10
        
        # Logging to file
        import logging
        logging.basicConfig(filename='robot.log', level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def health_check(self):
        # Check node health
        if not self.is_healthy():
            self.error_count += 1
            self.logger.error(f'Health check failed: {self.error_count}')
            
            if self.error_count >= self.max_errors:
                self.emergency_stop()
        else:
            self.error_count = 0
    
    def is_healthy(self):
        # Check critical components
        checks = [
            self.camera_ok(),
            self.robot_ok(),
            self.planning_ok()
        ]
        return all(checks)
    
    def emergency_stop(self):
        self.logger.critical('Emergency stop triggered')
        # Send stop command to robot
        # Notify operators
        # Safely shutdown
```

---

## 6.8 Best Practices

### 6.8.1 Code Organization

```
capstone_ws/
├── src/
│   ├── capstone_description/    # URDF, meshes, config
│   ├── capstone_gazebo/         # Simulation worlds, launch
│   ├── capstone_vision/         # Vision processing
│   ├── capstone_planning/       # Task & motion planning
│   ├── capstone_control/        # Robot control
│   ├── capstone_bringup/        # System launch files
│   └── capstone_msgs/           # Custom message definitions
└── docs/
    ├── README.md
    ├── API.md
    ├── ARCHITECTURE.md
    └── TROUBLESHOOTING.md
```

### 6.8.2 Documentation Standards

**Every package should have**:
- **README.md**: Purpose, dependencies, quickstart
- **package.xml**: Proper dependencies and metadata
- **Inline comments**: Explain complex logic
- **Type hints**: For Python code
- **Docstrings**: For all classes and functions

### 6.8.3 Version Control

```bash
# Use semantic versioning
git tag v1.0.0

# Meaningful commit messages
git commit -m "feat: add object detection node"
git commit -m "fix: resolve camera calibration issue"
git commit -m "docs: update API documentation"

# Branch strategy
main           # Production-ready
develop        # Integration
feature/vision # Feature branches
```

### 6.8.4 Continuous Integration

```yaml
# .github/workflows/ci.yml
name: ROS 2 CI

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup ROS 2
        uses: ros-tooling/setup-ros@v0.6
        with: