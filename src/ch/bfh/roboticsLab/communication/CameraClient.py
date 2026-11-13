'''
Copyright (C) BFH roboticsLab
All rights reserved.
'''
from ch.bfh.roboticsLab.communication.gRPC_Client import Client, Requester, Subscriber, request, checkConnected
from ch.bfh.roboticsLab.driver.Camera import VisionObjects
from ch.bfh.roboticsLab.vision import Vision_pb2 as pbVision
from ch.bfh.roboticsLab.vision import Vision_pb2_grpc as gpbVision
from google.protobuf.empty_pb2 import Empty
import numpy as np

import threading

class ImageSubscriber(Subscriber):
  def __init__(self, host, port, name, timeout = 5):
    super().__init__(gpbVision.ImagePublisherStub, host, pbVision.Image, port, timeout, name=name)
    self.updateCondition = threading.Condition()
    self.image = pbVision.Image()
    self.setProcessSubscriptionCallback(self.processSubscription)
  
  def processSubscription(self, message:pbVision.Image):
    with self.updateCondition:
      self.image.CopyFrom(message)
      self.updateCondition.notify_all()
      
  def getImage(self) -> pbVision.Image:
    with self.updateCondition:
      return self.image

class ObjectSubscriber(Subscriber):
  def __init__(self, host, port, name, timeout = 5):
    super().__init__(gpbVision.ObjectListPublisherStub, host, pbVision.ObjectList, port, timeout,name=name)
    self.updateCondition = threading.Condition()
    self.objects = pbVision.ObjectList()
    self.setProcessSubscriptionCallback(self.processSubscription)
  
  def processSubscription(self, message:pbVision.ObjectList):
    with self.updateCondition:
      self.objects.Clear()
      self.objects.CopyFrom(message)
      self.updateCondition.notify_all()
      
  def getObjects(self) -> pbVision.ObjectList:
    with self.updateCondition:
      return self.objects
    
class CameraRequester(Requester):
  def __init__(self, host, port = None, name = 'Camera Requester'):
    super().__init__(gpbVision.CameraResponderStub, host, port, name)

class CameraClient(Client):
  def __init__(self, name, subscriber:list[Subscriber]=None, requester:Requester=None):
    super().__init__(name, subscriber, requester)
    self.cameraSubscribers = {}
    for s in subscriber:
      self.cameraSubscribers[s.name] = s

  def _convertImage(self, image: pbVision.Image) -> tuple[np.ndarray, float]:

    match image.format:
      case pbVision.Image.Format.RGB8:
        array = np.uint8(np.frombuffer(image.imageData, dtype=np.byte).reshape((image.height, image.width, 3)))
      case _: raise NotImplementedError(f'Format not implemented: {image.format}')

    return array, image.timestamp

  @checkConnected
  def getImage(self,subscriberName:str, block: bool = False) -> tuple[np.ndarray, float]:
    sub = self.cameraSubscribers[subscriberName]
    assert isinstance(sub, ImageSubscriber)
    if not sub.isConnected():
      raise RuntimeWarning(f'Subscriber {subscriberName} not connected')
    if block:
      with sub.updateCondition:
        if not sub.updateCondition.wait(1):
          return None, None
    return self._convertImage(sub.getImage())
  
  @checkConnected
  def getObjects(self,subscriberName:str, block: bool = False) -> list[VisionObjects]:
    sub = self.cameraSubscribers[subscriberName]
    assert isinstance(sub, ObjectSubscriber)
    if not sub.isConnected():
      raise RuntimeWarning(f'Subscriber {subscriberName} not connected')
    if block:
      with sub.updateCondition:
        if not sub.updateCondition.wait(1):
          return []
    objects = sub.getObjects()
    objectList:list[VisionObjects] = []
    for o in objects.objects:
      objectList.append(VisionObjects.fromProto(o))
    return objectList

  @request
  def requestImage(self) -> np.ndarray:
    """Get the latest image from the image server.
    Use as an alternative ImagePublisher to poll for Images.
    """
    image = self.requester.requester.getImage(pbVision.GetImage())
    return self._convertImage(image=image)

  @request
  def clearObjects(self) -> None:
    """Clears all the objects from the server
    """
    ack = self.requester.requester.clearObjects(Empty)

    return None
  
  @request
  def trackObject(self, request: pbVision.ObjectTracking) -> pbVision.ObjectList:
    print('trackObject')
    objectList = self.requester.requester.trackObject(request)
    return objectList