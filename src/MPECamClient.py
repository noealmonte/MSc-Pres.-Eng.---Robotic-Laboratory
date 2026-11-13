'''
MPE Control & Automation
Python interface to the SVS camera.
@author gabriel.gruener@bfh.ch
@author gionata.quadri@bfh.ch
'''

import time
import numpy as np
from enum import Enum, auto
import json
from typing import Literal
from ch.bfh.roboticsLab.communication.CameraClient import CameraClient, ImageSubscriber, ObjectSubscriber, CameraRequester, pbVision
from ch.bfh.roboticsLab.driver.Camera import VisionObjects
import traceback


CAM_192_168_0_100_SN = '132902'
CAM_192_168_0_101_SN = '132903'


class Requests(Enum):
  '''
  This class holds an enumeration of known camera requests.
  '''
  GET_LASER_POINT = auto()
  START_TRAJECTORY = auto()
  END_TRAJECTORY = auto()


class MpeCamClient(CameraClient):
  '''
  Master in precision engineering SVS camera client
  Connects to a grpc server publishing the position of the laser on the camera sensor.
  '''

  def __init__(self, name, robotIP: Literal['192.168.0.100', '192.168.0.101']):
    CAM_192_168_0_100_IMG_PUB_PORT = 40850
    CAM_192_168_0_100_OBJ_PUB_PORT = 40860
    CAM_192_168_0_100_OBJ_RESP_PORT = 40870

    CAM_192_168_0_101_IMG_PUB_PORT = 40851
    CAM_192_168_0_101_OBJ_PUB_PORT = 40861
    CAM_192_168_0_101_OBJ_RESP_PORT = 40871

    HOST = '192.168.0.25'

    # Create a object subscriber and camera requester
    # imgPubPort = CAM_192_168_0_100_IMG_PUB_PORT if '192.168.0.100' == robotIP else CAM_192_168_0_101_IMG_PUB_PORT
    objPubPort = CAM_192_168_0_100_OBJ_PUB_PORT if '192.168.0.100' == robotIP else CAM_192_168_0_101_OBJ_PUB_PORT
    respPubPort = CAM_192_168_0_100_OBJ_RESP_PORT if '192.168.0.100' == robotIP else CAM_192_168_0_101_OBJ_RESP_PORT

    subscribers = [
        # ImageSubscriber(host=HOST,port=imgPubPort, name='ImageSubscriber'),
        ObjectSubscriber(host=HOST, port=objPubPort, name='ObjectSubscriber'),
    ]
    requester = CameraRequester(HOST, respPubPort)
    super().__init__(name, subscribers, requester)


class Location:
  '''
  This class holds the location of a detected object on the camera image.
  '''

  def __init__(self, u=np.nan, v=np.nan, x=np.nan, y=np.nan, timestamp=np.nan, SN=''):
    '''
    Creats a new location object.

    :param float u: horizontal location of detected object [px], defaults to np.nan
    :param float v: vertical location of detected object [px], defaults to np.nan
    :param float x: horizontal location of detected object [mm], defaults to np.nan
    :param float y: vertical location of detected object [px], defaults to np.nan
    :param float timestamp: Unix timestamp of the measurement, defaults to np.nan
    :param str SN: Camera serial number as ID, defaults to ''
    '''
    self.u = u
    '''Laser horizontal location on the image plane in px'''
    self.v = v
    '''Laser vertical location on the image plane in px'''
    self.x = x
    '''Laser horizontal location on the camera sensor in mm'''
    self.y = y
    '''Laser vertical location on the camera sensor in mm'''
    self.timestamp = timestamp
    '''timestamp of the image used to detect the laser location'''
    self.SN = SN
    '''Camera serial number or detected object name'''

  @classmethod
  def fromDict(cls, point: dict[str, any]):
    '''
    Create a new Location object from a data dictionary.

    :param dict point: Dictionary.
    :return Location: Location object.
    '''
    return cls(point['u'], point['v'], point['x'], point['y'], point['timestampEpoch'], point['serial_number'])

  @classmethod
  def fromObject(cls, object: VisionObjects):
    '''
    Create a new Location object from a published Vision object

    :param VisionObjects object: Vision object describing the laser point location.
    :return Location: Location object.
    '''
    x, y, _, _, _, _, = object.pose.toArrayWithFixedAngles()
    return cls(np.nan, np.nan, x, y, object.timestamp, object.id)

  def __str__(self):
    ''' Create a string representation of this Localization object. '''
    return str(self.__dict__)


class Trajectory:
  '''
  This class represents an object trajectory as a list of Locations.
  '''

  def __init__(self, trajectory: list[Location] = []):
    '''
    Create a new Trajectory object.

    :param list[Location] trajectory: A list of Locations, defaults to []
    '''
    self.trajectory: list[Location] = trajectory

  @classmethod
  def fromJSON(cls, jsonData: bytes):
    '''
    Create a new Trajectory object from a json data set.

    :param bytes jsonData: Trajectory data.
    :return Trajectory: Trajectory object.
    '''
    data = json.loads(jsonData)
    traj = data['trajectory']
    trajList = [Location.fromDict(point) for point in traj]
    return cls(trajList)

  @classmethod
  def fromObjectList(cls, objectList: pbVision.ObjectList):
    '''
    Create a new Trajectory object from a published object List

    :param pbVision.ObjectList objectList: Trajectory data.
    :return Trajectory: Trajectory object.
    '''
    trajList = [Location.fromObject(VisionObjects.fromProto(point)) for point in objectList.objects]
    return cls(trajList)

  def __str__(self):
    ''' Create a string representation of this Trajectory object. '''
    return '\n'.join([str(point) for point in self.trajectory])


class SVS:
  '''
  This class implements a client to the SVS camera server and reads the location or trajectory of a detected laser point center.
  '''

  def __init__(self, robotIP: Literal['192.168.0.100', '192.168.0.101']):
    '''
    Creates a new SVS client object.

    :param str robotIP: IP address of the robot to define the camera serial number to use.
    '''
    self.client = MpeCamClient(robotIP, robotIP)
    self.camSN = CAM_192_168_0_100_SN if robotIP[-1] == '0' else CAM_192_168_0_101_SN

  def getLaserLocation(self) -> Location:
    '''
    Retrieve the last detected laser point location.

    :return Location|None: Detected laser point location or None if the laser is not detected.
    '''
    objects: list[VisionObjects] = self.client.getObjects('ObjectSubscriber', block=True)
    index = None
    for i, o in enumerate(objects):
      if o.id == 'laser':
        index = i
        break

    if index is None:
      return None
    else:
      print(objects[index])
      location = Location.fromObject(objects[index])
      return location

  def startTrajRecord(self):
    '''
    Starts a thread recording the laser trajectory on the server side.
    The path is saved in a circular buffer containing a maximum of 500 laser locations.

    Call self.endTrajRecord() to stop the thread and get the trajectory
    '''
    self.client.trackObject(request=pbVision.ObjectTracking(id='laser', track=True))

  def endTrajRecord(self) -> Trajectory:
    '''
    Stop recording a trajectory and return the recorded data.

    :return Trajectory|None: Recorded trajectory or None if the laser was not detected during the recording.
    '''
    recordedPoints = self.client.trackObject(request=pbVision.ObjectTracking(id='laser', track=False))
    return Trajectory.fromObjectList(recordedPoints)

  def shutdown(self):
    '''
    Stop and disconnect the SVS camera client.
    '''
    self.client.shutdown()


if __name__ == '__main__':
  client = SVS('192.168.0.100')
  client.shutdown()
