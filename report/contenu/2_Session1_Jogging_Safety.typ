= Session 1 - Meca500
== Product information

The used robot for this laboratory work is the Meca500 from Mecademic. According to the brochure @ref:Meca500-brochure the robot is the world's smallest, most compact and the most precise six-axis industrial robot arm. In fact, again according to @ref:Meca500-brochure, the robot reaches a repetability of $5mu m$, has its controller embedded in the base and it is 2 times smaller than comparable market options. The power consumption is also a good point to consider, it consumes only 30w comparing to the LR Mate 200iD from fanuc, it consumes roughly 16 times less. In addition this robot is really versatile in its applications and easy to integrate and assemble due to the fact that it can be mounted in any orientation and with a high versatility of end-of-arm tooling. The brochure @ref:Meca500-brochure shows a sample of what can be mounted:
- Electrical parallel grippers
- dry adhesion gripper
- pneumatic module


Observations: Super silent

Question 1.2.3 : $theta 1 = -175degree$ to $175 degree$
$theta 2 = -70degree$ to $90 degree$
$theta 3 = -135degree$ to $70 degree$
$theta 4 = -170degree$ to $170 degree$
$theta 5 = -115degree$ to $115 degree$
$theta 6 = -720degree$ to $720 degree$

Question 1.2.4 : /worldFrame x: 329.2652 mm
y: 329.2652 mm
z: 464.4371 mm
yes, even in a plane

= Session 1: Safety, Jogging & Python Socket Interface

== Safety Procedures & Emergency Stop
Prior to commissioning the manipulator, the physical and software emergency stop (E-stop) mechanisms were tested.

#figure(
  caption: [Summary of Safety Interlocks and Operational Boundaries],
  table(
    columns: (1.5fr, 3fr),
    align: (left, left),
    table.header([*Element*], [*Description / Operational Behavior*]),
    [E-Stop Button], [Immediate power cutoff to joint servomotors, engaging mechanical brakes.],
    [Software Limits],
    [Enforced joint angle boundaries ($theta_i^("min") <= theta_i <= theta_i^("max")$) preventing mechanical collisions.],

    [Collision Detection],
    [Torque/current thresholds triggering automatic safe stop upon unexpected physical resistance.],
  ),
)

== Joint Jogging vs. Cartesian Jogging
The robot motion was tested using both joint-space commands (`moveJoints`) and Cartesian-space commands (`moveLin`, `movePose`):
- *Joint Jogging*: Directly drives individual revolute joints $theta_1$ through $theta_6$. Non-linear tool tip trajectory, but immune to internal kinematic singularities.
- *Cartesian Jogging*: Computes continuous inverse kinematics to move the end-effector along linear paths or maintain fixed orientations relative to the world reference frame ${W}$.

== Python Socket Communication
A dedicated Python socket wrapper (`Meca500.py`) connects to the robot controller via port 10000.

```python
from Meca500 import Meca500

# Connect to robot controller
meca = Meca500(ipAddress="192.168.0.100")
meca.activate()
meca.home()

# Set joint velocity limit (safety baseline: 5%)
meca.setJointVelocity(velocity=5)
meca.setBlending(0)

# Query current state
joints = meca.getJoints()
pose = meca.getPose()
print(f"Joints: {joints}, Pose: {pose}")
```
