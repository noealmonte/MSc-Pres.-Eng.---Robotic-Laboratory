= Session 2: Forward Kinematics & Tool Center Point (TCP)

== Coordinate Frame Definitions
To establish the geometric relationship between the robot base frame ${B}$ and the end-effector tool frame ${T}$, coordinate frames are assigned according to the standard robotics convention.

$
  ^0 T_6 = A_1(theta_1) dot A_2(theta_2) dot A_3(theta_3) dot A_4(theta_4) dot A_5(theta_5) dot A_6(theta_6)
$

== Symbolic Kinematics with SymPy
Symbolic derivation was implemented in Python using the `sympy` library. Homogeneous transformation matrices $T_i^(i-1)$ are constructed symbolically as functions of the joint angles $theta_i$.

== Tool Center Point (TCP) Calibration
The laser tool mounted on the flange introduces a linear offset along the $Z_6$ axis:

$
  ^6 T_("TCP") = mat(
    1, 0, 0, 0;
    0, 1, 0, 0;
    0, 0, 1, d_z;
    0, 0, 0, 1
  )
$

Where $d_z = 264 "mm"$ according to the mechanical drawing (`LaserTool.pdf`).
