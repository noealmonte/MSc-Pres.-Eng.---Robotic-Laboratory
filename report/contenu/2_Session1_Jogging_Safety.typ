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
    [Software Limits], [Enforced joint angle boundaries ($theta_i^("min") <= theta_i <= theta_i^("max")$) preventing mechanical collisions.],
    [Collision Detection], [Torque/current thresholds triggering automatic safe stop upon unexpected physical resistance.]
  )
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
