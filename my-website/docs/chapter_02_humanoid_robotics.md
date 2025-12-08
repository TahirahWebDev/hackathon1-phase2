# Chapter 2: Basics of Humanoid Robotics

## Learning Objectives

By the end of this chapter, you will be able to:
- Understand the mechanical structure and design principles of humanoid robots
- Explain forward and inverse kinematics for robotic manipulators
- Identify different types of actuators and their trade-offs
- Describe sensor integration for perception and proprioception
- Understand basic control architectures for humanoid systems
- Recognize the challenges unique to bipedal locomotion

---

## 2.1 Why Humanoid Robots?

Humanoid robots are designed to mimic the human form—typically featuring a torso, two arms, two legs, and a head. But why build robots that look like humans?

### Advantages of Human-Like Form

**1. Human-Designed Environments**
Our world is built for humans: doorways, stairs, chairs, tools, and vehicles all assume a human body shape. A humanoid robot can navigate these spaces and use these tools without requiring environmental modifications.

**2. Natural Human Interaction**
Humans are more comfortable interacting with entities that resemble them. Humanoid robots can use gestures, facial expressions, and body language for intuitive communication.

**3. Versatility & Generalization**
A humanoid form factor enables a single platform to perform diverse tasks—from opening doors to operating machinery to assisting with daily activities—without specialized end-effectors.

**4. Leveraging Human Data**
Humanoid robots can learn from human demonstrations more directly. Motion capture data, teleoperation, and imitation learning become more straightforward when the robot has a similar kinematic structure.

### Notable Humanoid Robots

- **ASIMO** (Honda): Early pioneer, demonstrated walking, running, stair climbing
- **Atlas** (Boston Dynamics): Athletic capabilities, parkour, backflips
- **Optimus** (Tesla): Designed for factory and household tasks
- **Figure 01** (Figure AI): General-purpose humanoid for commercial deployment
- **Digit** (Agility Robotics): Warehouse logistics and delivery
- **NAO** (SoftBank): Educational and research platform
- **Pepper** (SoftBank): Social interaction and customer service

---

## 2.2 Mechanical Structure & Degrees of Freedom

### 2.2.1 Kinematic Chain

A humanoid robot is composed of **rigid links** connected by **joints**. This forms a kinematic chain where motion at one joint affects the position of all subsequent links.

**Key Terminology**:
- **Link**: Rigid body segment (e.g., forearm, thigh)
- **Joint**: Connection allowing relative motion between links
- **Degree of Freedom (DOF)**: Independent motion capability (e.g., shoulder rotation)
- **End-effector**: Terminal link (e.g., hand, foot)

### 2.2.2 Typical DOF Distribution

A full humanoid robot typically has 30-50+ DOF:

**Head** (2-3 DOF):
- Yaw (side-to-side)
- Pitch (up-down)
- Roll (tilt) [optional]

**Torso** (1-3 DOF):
- Waist yaw
- Spine pitch/roll [optional]

**Arms** (7 DOF each = 14 total):
- Shoulder: 3 DOF (pitch, roll, yaw)
- Elbow: 1 DOF (flexion/extension)
- Wrist: 3 DOF (pitch, roll, yaw)
- Hand: 1-20+ DOF depending on complexity

**Legs** (6 DOF each = 12 total):
- Hip: 3 DOF (pitch, roll, yaw)
- Knee: 1 DOF (flexion/extension)
- Ankle: 2 DOF (pitch, roll)

**Total**: ~30-40 DOF for basic humanoid, 50+ with articulated hands

### 2.2.3 Joint Types

**Revolute Joint (Hinge)**
- Rotates around a single axis
- Most common in humanoid robots
- Examples: elbow, knee, finger joints

**Prismatic Joint (Slider)**
- Translates along a single axis
- Less common in humanoids
- Examples: telescoping limbs, spinal extension

**Spherical Joint (Ball-and-Socket)**
- 3 DOF rotation around a point
- Mechanically complex to implement
- Often approximated with 3 revolute joints (shoulder, hip)

---

## 2.3 Kinematics: The Mathematics of Motion

Kinematics describes the geometry of motion without considering forces. For humanoid robots, we need to solve two fundamental problems:

### 2.3.1 Forward Kinematics (FK)

**Problem**: Given joint angles θ₁, θ₂, ..., θₙ, what is the position and orientation of the end-effector?

**Solution**: Use transformation matrices to propagate from base to end-effector.

**Denavit-Hartenberg (DH) Convention**:
A systematic way to assign coordinate frames to each joint. Each link is described by 4 parameters:
- **a**: Link length
- **α**: Link twist
- **d**: Link offset
- **θ**: Joint angle (variable for revolute joints)

**Transformation Matrix**:
```
T = [cos(θ)  -sin(θ)cos(α)   sin(θ)sin(α)  a·cos(θ)]
    [sin(θ)   cos(θ)cos(α)  -cos(θ)sin(α)  a·sin(θ)]
    [0        sin(α)         cos(α)         d       ]
    [0        0              0              1       ]
```

**Chain Rule**: Multiply transformations from base to end-effector:
```
T_end = T₀₁ · T₁₂ · T₂₃ · ... · Tₙ₋₁,ₙ
```

**Example: 2-Link Planar Arm**

Given:
- Link 1 length: L₁ = 1.0 m, angle θ₁ = 45°
- Link 2 length: L₂ = 0.8 m, angle θ₂ = 30°

End-effector position:
```
x = L₁·cos(θ₁) + L₂·cos(θ₁ + θ₂)
y = L₁·sin(θ₁) + L₂·sin(θ₁ + θ₂)

x = 1.0·cos(45°) + 0.8·cos(75°) ≈ 0.914 m
y = 1.0·sin(45°) + 0.8·sin(75°) ≈ 1.480 m
```

### 2.3.2 Inverse Kinematics (IK)

**Problem**: Given desired end-effector position/orientation, what joint angles achieve it?

**Challenge**: Often has multiple solutions (or no solution if position unreachable).

**Approaches**:

**1. Analytical (Closed-Form)**
- Geometric reasoning to derive equations
- Fast computation
- Only feasible for simple kinematic chains (≤6 DOF)

**Example for 2-Link Planar Arm**:
```
θ₂ = ±arccos((x² + y² - L₁² - L₂²) / (2·L₁·L₂))
θ₁ = arctan2(y, x) - arctan2(L₂·sin(θ₂), L₁ + L₂·cos(θ₂))
```

**2. Numerical (Iterative)**
- **Jacobian-based methods**: Linearize and iterate
- **Optimization**: Minimize ||f(θ) - target||²
- Handles redundant systems (more DOF than needed)
- May get stuck in local minima

**3. Learning-Based**
- Train neural networks to predict joint angles
- Handles complex constraints
- Requires large datasets

### 2.3.3 Jacobian Matrix

The Jacobian J relates joint velocities to end-effector velocities:
```
ẋ = J(θ) · θ̇
```

Where:
- ẋ: End-effector velocity (linear + angular)
- θ̇: Joint velocities
- J(θ): Jacobian matrix (6×n for n joints)

**Applications**:
- Velocity control
- Singularity detection (det(J) = 0)
- Force control (τ = Jᵀ · F)

---

## 2.4 Actuation Systems

Actuators convert energy into motion. Choosing the right actuator involves trade-offs between power, speed, precision, size, and cost.

### 2.4.1 Electric Motors

**Brushed DC Motors**
- Simple control, low cost
- Wear due to brushes
- Used in hobbyist robots

**Brushless DC Motors (BLDC)**
- Higher efficiency, longer life
- Requires electronic commutation (ESC)
- Common in drones and small humanoids

**Servo Motors**
- Integrated position feedback and control
- Easy to use (PWM signal)
- Limited torque for humanoid applications

**Stepper Motors**
- Precise positioning without feedback
- Lower speed and efficiency
- Used in CNC and 3D printers

### 2.4.2 Hydraulic Actuators

**Advantages**:
- High power-to-weight ratio
- Large force output
- Used in Atlas (Boston Dynamics)

**Disadvantages**:
- Complex system (pump, valves, reservoir)
- Messy (oil leaks)
- Difficult to control precisely
- Noisy operation

### 2.4.3 Pneumatic Actuators

**Advantages**:
- Safe (compliant, no electrical hazard)
- Fast response
- Low cost

**Disadvantages**:
- Compressibility makes control difficult
- Requires air supply
- Limited force compared to hydraulics
- Noisy

### 2.4.4 Series Elastic Actuators (SEA)

**Design**: Spring in series between motor and load

**Advantages**:
- Compliant, safe for human interaction
- Force sensing via spring deflection
- Energy storage for dynamic motions
- Used in many research humanoids

**Disadvantages**:
- Lower bandwidth (spring introduces lag)
- More complex mechanical design

### 2.4.5 Comparison Table

| Actuator Type | Power Density | Speed | Precision | Cost | Typical Use |
|---------------|---------------|-------|-----------|------|-------------|
| Brushed DC | Low | Medium | Low | Low | Toys, hobbyist |
| BLDC | Medium | High | Medium | Medium | Drones, arms |
| Hydraulic | Very High | Medium | Low | High | Heavy-duty (Atlas) |
| Pneumatic | Medium | High | Low | Low | Soft robots |
| SEA | Medium | Low | High | High | Research humanoids |

---

## 2.5 Sensor Integration

Humanoid robots require diverse sensors for perception and state estimation.

### 2.5.1 Proprioceptive Sensors (Internal State)

**Joint Encoders**
- Measure joint angles
- Types: Incremental, absolute
- Resolution: 12-bit to 20-bit

**Inertial Measurement Unit (IMU)**
- 3-axis accelerometer: linear acceleration
- 3-axis gyroscope: angular velocity
- 3-axis magnetometer (optional): absolute heading
- Used for balance and orientation estimation

**Force/Torque Sensors**
- Measure interaction forces
- Locations: feet (ground contact), wrists (manipulation), joints (load)
- Enables compliant control and safety monitoring

**Current Sensors**
- Monitor motor currents
- Indirectly measure torque (τ ≈ k · I)
- Detect collisions and overloads

### 2.5.2 Exteroceptive Sensors (External Environment)

**Cameras**
- RGB: Color images for object recognition
- Depth: Stereo, structured light, or time-of-flight
- Typical placement: head (binocular vision), hands (manipulation)

**LIDAR**
- 2D or 3D point clouds
- Long range (10-100m)
- Robust to lighting conditions
- Used for mapping and obstacle avoidance

**Ultrasonic Sensors**
- Short-range proximity detection (0.1-5m)
- Low cost, simple interface
- Used for basic obstacle avoidance

**Tactile Sensors**
- Pressure/touch detection
- Important for manipulation (e.g., object grasping)
- Complex and expensive to integrate

### 2.5.3 Sensor Fusion

Combining multiple sensors improves robustness:

**Kalman Filter**
- Optimal fusion under Gaussian noise
- Used for pose estimation (IMU + encoders)

**Particle Filter**
- Handles non-Gaussian distributions
- Used for localization (cameras + LIDAR)

**Complementary Filter**
- Simple, lightweight fusion
- Common for IMU orientation estimation

---

## 2.6 Control Architectures

### 2.6.1 Hierarchical Control Structure

Humanoid robots typically use a layered control architecture:

```
┌─────────────────────────────────────┐
│   High-Level Planning               │  <- Task/behavior planning
│   (seconds to minutes)              │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│   Mid-Level Control                 │  <- Trajectory generation
│   (100-500 Hz)                      │     Inverse kinematics
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│   Low-Level Control                 │  <- Motor control (PID)
│   (1-10 kHz)                        │     Force/torque control
└─────────────────────────────────────┘
```

### 2.6.2 PID Control

**Proportional-Integral-Derivative** control is the workhorse of robotics:

```
u(t) = Kₚ·e(t) + Kᵢ·∫e(t)dt + Kd·de(t)/dt
```

Where:
- e(t) = reference - actual (error)
- Kₚ: Proportional gain (immediate response)
- Kᵢ: Integral gain (eliminate steady-state error)
- Kd: Derivative gain (damping, reduce overshoot)

**Tuning**:
- Start with Kₚ only, increase until oscillations
- Add Kd to dampen oscillations
- Add Kᵢ to eliminate steady-state error
- Iterate and test

### 2.6.3 Impedance Control

For safe human-robot interaction, control both position and force:

```
F = K·(x_desired - x_actual) + B·(ẋ_desired - ẋ_actual)
```

Where:
- K: Stiffness (spring constant)
- B: Damping (resistance to velocity)

**Benefits**:
- Compliant behavior
- Safe contact with humans and environment
- Natural-feeling interactions

### 2.6.4 Model Predictive Control (MPC)

Optimize control over a future horizon:

1. Predict future states using a model
2. Optimize control inputs to minimize cost
3. Apply first control input
4. Repeat (receding horizon)

**Advantages**:
- Handles constraints (joint limits, torque limits)
- Anticipates future states
- Optimal trajectories

**Disadvantages**:
- Computationally expensive
- Requires accurate model
- Tuning can be complex

---

## 2.7 Bipedal Locomotion

Walking on two legs is one of the hardest problems in humanoid robotics.

### 2.7.1 Static vs. Dynamic Walking

**Static Walking**
- Center of Mass (CoM) always above support polygon
- Slow, stable
- Easy to control
- Energy inefficient

**Dynamic Walking**
- CoM can momentarily leave support polygon
- Faster, more natural
- Requires active balance control
- Energy efficient (passive dynamics)

### 2.7.2 Zero Moment Point (ZMP)

The ZMP is the point on the ground where the net moment from gravity and inertia is zero.

**Stability Condition**: ZMP must stay inside the support polygon (foot contact area).

**ZMP-Based Walking**:
1. Plan CoM trajectory such that ZMP stays inside support polygon
2. Compute inverse kinematics for leg joints
3. Execute trajectory with feedback control

**Limitations**:
- Conservative (always statically stable)
- Cannot handle dynamic maneuvers (running, jumping)

### 2.7.3 Gait Patterns

**Walk Cycle Phases**:
1. **Double Support**: Both feet on ground
2. **Single Support**: One foot on ground, other swinging
3. **Swing Phase**: Foot moves forward
4. **Heel Strike**: Foot touches down

**Key Parameters**:
- Step length: Distance between foot placements
- Step width: Lateral spacing
- Step height: Swing foot clearance
- Step time: Duration of one step

### 2.7.4 Balance & Stabilization

**Ankle Strategy**
- Small perturbations
- Torque at ankles to adjust CoM
- Fast, minimal motion

**Hip Strategy**
- Larger perturbations
- Torque at hips to move CoM
- Slower, more motion

**Stepping Strategy**
- Very large perturbations
- Take a step to regain balance
- Last resort, most effective

---

## 2.8 Challenges in Humanoid Robotics

### 1. Complexity
- 30-50 DOF to coordinate simultaneously
- Coupled dynamics (moving one limb affects whole body)
- Real-time computation requirements

### 2. Energy Efficiency
- Humanoid walking is energy-intensive
- Battery life limits autonomy (typically 1-2 hours)
- Optimization of gait and control crucial

### 3. Robustness
- Uneven terrain, obstacles, disturbances
- Slip detection and recovery
- Fall detection and mitigation

### 4. Manipulation
- Dexterous grasping requires complex hands
- Coordination of arm, wrist, and fingers
- Force control to avoid damaging objects

### 5. Perception
- Real-time processing of visual and depth data
- Occlusions and lighting variations
- Integration with control (closed-loop)

### 6. Cost
- High-quality actuators and sensors are expensive
- Custom mechanical design and fabrication
- Research platforms cost $100K-$1M+

---

## 2.9 Design Example: Simplified Humanoid Arm

Let's design a basic 3-DOF arm for manipulation tasks.

### Specifications
- Reach: 0.8 m
- Payload: 2 kg
- Precision: ±5 mm

### Kinematic Design
- **Joint 1** (Shoulder Pitch): 0° to 180°
- **Joint 2** (Elbow Pitch): 0° to 150°
- **Joint 3** (Wrist Roll): -90° to 90°

### Link Lengths
- Upper arm: L₁ = 0.4 m
- Forearm: L₂ = 0.4 m

### Actuator Selection
- Joints 1-2: BLDC motors with 50:1 gearbox (high torque)
- Joint 3: Small servo motor (low torque, wrist rotation)

### Sensors
- Encoders: 14-bit absolute (0.02° resolution)
- 6-axis IMU in forearm (orientation feedback)
- Force/torque sensor at wrist (manipulation tasks)

### Control
- Low-level: PID joint control at 1 kHz
- Mid-level: Inverse kinematics at 100 Hz
- High-level: Task planner (pick-and-place, handover)

---

## 2.10 Chapter Summary

Humanoid robots are designed with human-like form to navigate our environments and interact naturally. They consist of rigid links connected by joints, typically totaling 30-50 degrees of freedom across head, torso, arms, and legs.

Forward kinematics computes end-effector position from joint angles using transformation matrices, while inverse kinematics solves for joint angles given a desired position. The Jacobian matrix relates joint velocities to end-effector velocities.

Actuation options include electric motors (BLDC, servos), hydraulic actuators (high power), pneumatic systems (compliant), and series elastic actuators (safe interaction). Each has trade-offs in power, speed, precision, and cost.

Sensors are divided into proprioceptive (encoders, IMUs, force sensors) for internal state and exteroceptive (cameras, LIDAR) for environment perception. Sensor fusion techniques like Kalman filters combine data for robust estimation.

Control architectures are hierarchical: high-level planning, mid-level trajectory generation, and low-level motor control. PID control is standard, with impedance control for safe interaction and MPC for optimal trajectories.

Bipedal locomotion is challenging, requiring balance control through ZMP planning or dynamic approaches. Walking involves gait patterns, balance strategies, and robustness to disturbances.

Key challenges include complexity, energy efficiency, robustness, dexterous manipulation, real-time perception, and high costs. Despite these challenges, humanoid robotics continues to advance, driven by applications in manufacturing, healthcare, and service domains.

---

## Key Takeaways

✅ Humanoid robots navigate human environments using human-like morphology  
✅ Forward kinematics: joint angles → end-effector position  
✅ Inverse kinematics: desired position → joint angles (multiple solutions)  
✅ Actuators: BLDC motors common, hydraulics for power, SEA for safety  
✅ Sensors: Encoders + IMU (proprioception), cameras + LIDAR (exteroception)  
✅ Control: Hierarchical (planning → trajectories → motor control)  
✅ Bipedal walking: ZMP-based (stable) or dynamic (efficient)  
✅ Challenges: complexity, energy, robustness, manipulation, perception, cost  

---

## Further Reading

- **Books**:
  - "Introduction to Robotics: Mechanics and Control" by John J. Craig
  - "Springer Handbook of Robotics" (Chapter on Humanoid Robots)
  - "Humanoid Robotics: A Reference" by Ambarish Goswami and Prahlad Vadakkepat

- **Papers**:
  - "The Spring-Mass Model for Running and Hopping" (Blickhan, 1989)
  - "Biped Walking Pattern Generation by using Preview Control of ZMP" (Kajita et al., 2003)

- **Online Resources**:
  - MIT OpenCourseWare: Underactuated Robotics
  - ROS 2 Control Tutorials
  - Boston Dynamics Technical Blog

---

**Next Chapter**: ROS 2 Fundamentals – We'll learn the software framework that integrates all these components into a working robotic system.