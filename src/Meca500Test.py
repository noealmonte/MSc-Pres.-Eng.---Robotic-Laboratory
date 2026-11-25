'''
MPE Control & Automation
Control a Meca500 robot with Python
@author gabriel.gruener@bfh.ch
'''

'''
DO NOT EXECUTE THIS SCRIPT FROM BEGINING TO END!
Run each section individually, observing carefully if the robot may safely move each time.
'''

#%% import packages
from Meca500 import Meca500
import time


#%% Create a Meca500 object and initialize the robot
print('Connecting...')
meca = Meca500(ipAddress="192.168.0.101")

print('Activating...')
meca.activate()
print('Homing...')
meca.home()


#%% Set the robot's velocity [%]
print('Setting joint velocity...')
meca.setJointVelocity(velocity=5)

meca.setBlending(0)


#%% Move the robot to some joint positions [deg]
theta = [0, 0, 0, 0, 0, 0]
print(f'Moving to {theta}')
meca.moveJoints(theta=theta)
meca.waitIdle()
# Read the current joint values
print(meca.getJoints())
# Read the current robot pose
print(meca.getPose())
meca.moveJoints(theta=[45, 0, 0, 0, 0, 0])
meca.moveJoints(theta=[45, 30, 30, 0, 30, 0])
time.sleep(1)
meca.moveJoints(theta=[45, 0, 0, 0, 0, 0])
meca.moveJoints(theta=[0, 0, 0, 0, 0, 0])
meca.waitIdle()


#%% Move the robot in joint space to a Cartesian pose
meca.moveJointsToPose(position=[120, 0, 200], orientation=[-180, 0, 180])
meca.waitIdle()
meca.moveJoints(theta=[0, 0, 0, 0, 0, 0])
meca.waitIdle()

#%% Set the Tool Center Point
# Sets the TCP one centimeter in front of the robot flange
meca.setToolOffset(position=[0, 0, 10], orientation=[0, 0, 0])


#%% Set the Cartesian linear velocity [mm/s]
meca.setCartesianLinearVelocity(velocity=10)
meca.moveCartesian(position=[120, 0, 200], orientation=[-180, 0, 180])
meca.waitIdle()

#%% Reset any robot errors
meca.reset()


#%% Disconnect from the robot controller
print('Deactivating...')
meca.deactivate()

print('Disconnecting...')
meca.disconnect()
del meca

# %%
