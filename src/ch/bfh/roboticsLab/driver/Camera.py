'''
Copyright (C) BFH roboticsLab
All rights reserved.
'''

import time
import numpy as np
from typing import final
import threading
from abc import abstractmethod
from ch.bfh.roboticsLab.util.Thread import Thread
from ch.bfh.roboticsLab.vision import Vision_pb2 as pbVision
from ch.bfh.roboticsLab.util.TransformationMatrix import TransformationMatrix as tm


class VisionObjects:
  def __init__(self, id: str, pose: tm = None, visible: bool = None, timestamp: float = None, name: str = None, description: str = None, dimensions: list[float] = None, icon: np.ndarray = None):
    self.pose: tm = pose
    self.id: str = id
    '''The unique identifier for this type of object.'''
    self.visible: bool = visible
    '''Detection flag, if visible True'''
    self.timestamp: float = timestamp
    '''Object detection timestamp as defined in python time.time()'''
    self.name: str = name
    '''The English name of this object type.'''
    self.plural: str = None
    '''The English plural name of this object.'''
    self.description: str = description
    '''An english sentence describing the object'''
    self.dimensions: list[float] = dimensions
    '''The dimensions of this object. [lx,ly,lz]'''
    self.icon: np.ndarray = icon
    '''A representative image (icon) of a generic object of this type.'''

  @classmethod
  def fromProto(cls, visionObject: pbVision.Object):
    # TODO decode icon
    return cls(id=visionObject.type.id, pose=tm.fromPose(visionObject.pose), visible=visionObject.visible, timestamp=visionObject.timestamp, name=visionObject.type.name, description=visionObject.type.description, dimensions=[visionObject.type.dimensions.lX, visionObject.type.dimensions.lY, visionObject.type.dimensions.lZ])

  def __str__(self):
    return f'Object {self.name}:{self.id} - visible: {self.visible}  name: {self.name}  timestamp: {self.timestamp}\n pose: {self.pose}'


class Camera(Thread):
  '''
  This class implements an abstract base class for real or simulated cameras.
  Implementing classes must clearly document the capabilities of the camera, like available resolutions and maximum frame rate.
  '''

  def __init__(self, resolution: tuple[int, int] = (640, 480), frameRate: int = 30) -> None:
    '''
    Create a new Camera object with the specified resolution and frame rate.

    :param tuple[int, int] resolution: (width, height) of the frame, defaults to (640, 480).
    :param int frame_rate: Desired frame rate in frames per second, defaults to 30.
    '''
    if frameRate <= 0:
      raise ValueError('frameRate must be larger than 0')
    super().__init__(period=1. / frameRate, name='Camera Thread')
    self._image = np.ndarray([])
    '''Image as numpy array'''
    self._objects: list[VisionObjects] = []
    '''Current vision objects visible in the camera fov'''
    self._timestamp: float = -1
    '''Timestamp of the last image query'''
    self._imageLock = threading.Condition()
    # TODO not yet implemented
    self._resolution = resolution
    '''Desired camera query resolution'''

  def __del__(self) -> None:
    ''' Destroys this object. '''
    self.shutdown()

  @final
  def shutdown(self) -> None:
    ''' Shuts down the Camera object by stopping the image query thread and closing the device. '''
    self.stop()
    self.close()

  @abstractmethod
  def open(self) -> None:
    '''
    This abstract method allows implementing classes to creates, configure and start the actual camera device.
    Implementing classes must document whether calling this method is mandatory for correct functionality of the device.
    '''
    raise NotImplementedError

  @abstractmethod
  def close(self) -> None:
    '''
    This abstract method allows implementing class to close the actual camera device and release any related resources.
    Implementing classes must document whether calling this method is mandatory for correct functionality of the device.
    '''

  @final
  def _run(self) -> None:
    '''
    Implements `Thread._run()`
    Continuously queries the Camera object to deliver one image.
    The frequency of this query is defined by the requested frame rate in the class constructor.
    Implementing classes must implement `_queryImage()` and document what is the maximum frame rate.
    '''
    while self._waitForNextPeriod():
      with self._imageLock:
        self._image = self._queryImage()
        self._timestamp = time.time()
        self._objects = self._queryObjects()
        self._imageLock.notify_all()

  @abstractmethod
  def _queryImage(self) -> np.ndarray:
    '''
    Queries the camera device to deliver one image, blocking execution until the image is ready.
    Implementing classes must document whether this method raises any exceptions, for example if an error happens while communicating with the device.
    Implementing classes must document the maximum frame rate possible for their device, accounting for the execution time of this method's implementation.

    :return np.ndarray: The camera image as a numpy array (height x width x depth).
    '''
    raise NotImplementedError

  @abstractmethod
  def _queryObjects(self) -> list[VisionObjects]:
    '''
    Queries the camera device to deliver all visible/invisible objects.
    Implementing classes must document whether this method raises any exceptions, for example if an error happens while communicating with the device.
    Implementing classes must document the maximum frame rate possible for their device, accounting for the execution time of this method's implementation.

    :return list[VisionObjects]: All the objects present in the environment and visible, the key is the object id.
    '''
    raise NotImplementedError

  @final
  def getImage(self, query: bool = True, block: bool = False) -> tuple[np.ndarray, float]:
    '''
    Retrieve an image from the camera device.
    If the query thread is running (see `start()), this method returns immediately with the latest image delivered by the device.
    Otherwise, this method will request a new image from the device, waiting for image acquisition before returning the data.

    :param query bool:
    :return tuple[np.ndarray, float]: The image as a numpy array (height x width x depth) and the timestamp right after the query result.
    '''
    if self.isRunning() or not query:
      # Immediately return the last received image
      with self._imageLock:
        if block:
          if not self._imageLock.wait(2):
            raise RuntimeWarning('Image awaited 2 sec but condition never set, check camera_queryImage')
        if isinstance(self._image, np.ndarray):
          image = self._image.copy()
        else:
          image = None
          self._timestamp = -1
    else:
      # Query a new image and return
      with self._imageLock:
        self._image = self._queryImage()
        self._timestamp = time.time()
        if isinstance(self._image, np.ndarray):
          image = self._image.copy()
        else:
          image = None
          self._timestamp = -1
    return image, self._timestamp

  @final
  def getObjects(self, query: bool = True, block: bool = False) -> list[VisionObjects]:
    '''
    Retrieve the visible vision objects from the camera device.
    If the query thread is running (see `start()), this method returns immediately with the latest image delivered by the device.
    Otherwise, this method will request a new image from the device, waiting for image acquisition before returning the data.

    :param query bool:
    :return list[VisionObjects]: The list of the current visible VisionObjects
    '''
    if self.isRunning() or not query:
      # Immediately return the last received image
      with self._imageLock:
        if block:
          if not self._imageLock.wait(2):
            raise RuntimeWarning('Image awaited 2 sec but condition never set, check camera_queryImage')
        objects = self._objects.copy()
    else:
      # Query a new image and return
      with self._imageLock:
        self._objects = self._queryObjects()
        objects = self._objects.copy()
    return objects
