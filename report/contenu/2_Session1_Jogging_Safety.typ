= Session 1 - Meca500
== Product information

The used robot for this laboratory work is the Meca500 from Mecademic. According to the brochure @ref:Meca500-brochure the robot is the world's smallest, most compact and the most precise six-axis industrial robot arm. In fact, again according to @ref:Meca500-brochure, the robot reaches a repetability of $5mu m$, has its controller embedded in the base and it is 2 times smaller than comparable market options. The power consumption is also a good point to consider, it consumes only 30w comparing to the LR Mate 200iD from fanuc, it consumes roughly 16 times less. In addition this robot is really versatile in its applications and easy to integrate and assemble due to the fact that it can be mounted in any orientation and with a high versatility of end-of-arm tooling. The brochure @ref:Meca500-brochure shows a sample of what can be mounted:
- Electrical parallel grippers
- dry adhesion gripper
- pneumatic module

According to all those specifications, the robot could be use in the following indutrial applications:
- Assembly of microscopic pieces of medical devices
- Handling of small pieces in PCB assembly
- Handling of medical samples for testing

According to @ref:Meca500-brochure the rated payload the robot can carraying is 0.5kg. But in certain conditions the robot can handle a mass until 1kg at his maximum.

One added observation done during the testing phase is that the robot is super quiet comparing to others robot we worked with.

*Question 1.2.3 :*

The ranges of each joint measured are presented in the table @tab:range-motion-joint below. 

#figure(
  table(
    columns: 3,
    align: center,
    stroke: 0.5pt,
[*Joint*], [*Min*], [*Max*],
  [$theta_1$], [$-175 degree$], [$175 degree$],
  [$theta_2$], [$-70 degree$], [$90 degree$],
  [$theta_3$], [$-135 degree$], [$70 degree$],
  [$theta_4$], [$-170 degree$], [$170 degree$],
  [$theta_5$], [$-115 degree$], [$115 degree$],
  [$theta_6$], [$-720 degree$], [$720 degree$], 
  ),
  caption: [Ranges of motion of each joint]
)<tab:range-motion-joint>


*Question 1.2.4*

To the worldFrame the far away the TCP can move is:
- 329.2652 mm in x direction
- 329.2652 mm in y direction
- 464.4371 mm in z direction

Yes the TCP can be oriented along the three axis due to the 6 degrees of freedom. 3 are used to move the tcp in the space x-y-z and the others 3 are used to orient the TCP as we want.

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
