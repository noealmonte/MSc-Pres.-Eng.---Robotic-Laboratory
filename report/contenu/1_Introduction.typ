= Introduction

== Context and Objectives
This report presents the experimental laboratory work conducted between November and December 2026 as part of the *Robotics* component of the *Control and Automation* course.

The experimental platform relies on the *Mecademic Meca500* (r4), a micro 6-axis industrial articulated robot arm, equipped with a custom flange-mounted laser tool and monitored by a high-resolution *SVS-Vistek* industrial CMOS camera.

The key objectives of this laboratory are:
+ Familiarization with precision robotic manipulators, emergency stop safety protocols, and dual-mode interaction (web interface vs. direct Python TCP/IP sockets).
+ Derivation, symbolic implementation, and experimental validation of the robot's forward kinematics using *SymPy*, including Tool Center Point (TCP) offset compensation for the laser tool.
+ Quantitative evaluation of robot repeatability according to the *ISO 9283* standard, distinguishing unidirectional and bidirectional repeatability across distinct robot arm configurations (folded vs. stretched), and investigating the effects of Cartesian path corner blending and velocity.

== Experimental Setup & Hardware Specifications
The experimental setup comprises:
- *Robot Manipulator*: Mecademic Meca500 (6 revolute joints, rated repeatability of $5 mu m$).
- *End-Effector*: Custom laser diode assembly mounted on the tool flange ($d_z = 264 "mm"$).
- *Vision Measurement System*: SVS-Vistek `exo183MU3` monochrome CMOS sensor ($5496 times 3672$ pixels, pixel pitch $2.4 mu m$).
- *Control Architecture*: Standalone Python workstation communicating via TCP/IP sockets (`192.168.0.100`) and gRPC camera streams (`192.168.0.25:8080`).
