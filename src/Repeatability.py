'''
MPE Control & Automation
Test the repeatability of a Mecademic Meca500 robot with Python.
@author gionata.quadri@bfh.ch
'''

'''
DO NOT EXECUTE THIS SCRIPT FROM BEGINING TO END!
Run each section individually, observing carefully if the robot may safely move each time.
'''

#%% import packages
from Meca500 import Meca500
import time
import numpy as np
from matplotlib import pyplot as plt
from MPECamClient import SVS
from PlotEllipse import plotEllipse


#%% Create Meca500 and camera objects, initialize the robot
print('Connecting...')
robotIP = '192.168.0.100'
meca = Meca500(ipAddress=robotIP)
camera = SVS(robotIP=robotIP)

print('Activating...')
meca.activate()
print('Homing...')
meca.home()


#%% TODO: Implement the lab tasks


#%% Disconnect from the robot controller and camera
print('Deactivating...')
meca.deactivate()
camera.shutdown()

print('Disconnecting...')
del meca
del camera