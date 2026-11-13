'''
Copyright (C) BFH roboticsLab
All rights reserved.
'''

import grpc
import threading
import grpc._channel
from typing import Callable, Type

from ch.bfh.roboticsLab import Base_pb2 as pbBase
from ch.bfh.roboticsLab.util.Logger import Logger, Level
from grpc._channel import _InactiveRpcError, _MultiThreadedRendezvous


def request(func):
  def wrapper_func(*args, **kwargs):
    # Do something before the function.
    client: Client = args[0]
    # retry to connect to the server if the previous request failed
    # necessary as if the server restarts the client do not reconnect automatically
    if not client.requester._success:
      client.requester.connect()
    try:
      retVal = func(*args, **kwargs)
      client.requester._success = True
      return retVal
    except _InactiveRpcError as e:
      client.requester._success = False
      try:
        client.logger.warning(f'The server {e.details().split(sep="ipv4:")[1].split(sep=" ")[0][0:-1]} is currently: {e.code().name}')
      except Exception:
        raise RuntimeWarning(e)
    except Exception as e:
      client.requester._success = False
      raise e
      # Do something after the function.

  return wrapper_func


def checkConnected(func):
  def wrapper_func(*args, **kwargs):
    # Do something before the function.
    client: Client = args[0]
    # Check if the subscriber is connected
    if isinstance(client.subscriber, Subscriber) and not client.subscriber.isConnected():
      return None
    elif isinstance(client.subscriber, list):
      # TODO check that the desired subscriber is connected
      pass
    try:
      return func(*args, **kwargs)
    except Exception as e:
      raise e
  return wrapper_func


class Requester():
  def __init__(self, responderStub: Type, host: str, port: int = None, name:str = 'Requester'):
    self.requesterStub = responderStub
    self.name = name
    self.port = port
    self.host = host
    # variable to store if the previous request succeded
    self._success = False

  def connect(self):
    self.requesterChannel = grpc.insecure_channel(f'{self.host}:{self.port}')
    self.requester = self.requesterStub(self.requesterChannel)

  def close(self):
    self.requesterChannel.close()


class Subscriber():
  def __init__(self, publisherStub: Type, host: str, publishedMessage: Type = None, port: int = None, timeout: float = 5, name:str = 'Subscriber'):
    self.logger = Logger(name, level=Level.INFO)
    self.name = name
    self.publisherStub = publisherStub
    self.host = host
    self.message = publishedMessage
    self.callback = None
    self.port = port
    self.running = threading.Event()
    self.connectedEvent = threading.Event()
    self.reconnect = threading.Condition()
    self.connectedEvent.clear()
    self.running.set()
    self.channelOptions = [('grpc.max_receive_message_length', 10_000_000)]
    self.timeout = timeout
    self.subscriberChannel = grpc.insecure_channel(f'{self.host}:{self.port}', options=self.channelOptions)
    self.subscriber = self.publisherStub(self.subscriberChannel)
    self.reconnectThread = threading.Thread(target=self._reconnectHandler)
    self.reconnectThread.start()

  def setProcessSubscriptionCallback(self, processSubscription: Callable[[object], None]):
    self.callback = processSubscription

  def isConnected(self):
    return self.connectedEvent.is_set()

  def connect(self):
    self.subscription = self._subscribe()

    # Variables to save incoming subscription data
    self.published = self.message()
    self.publishedLock = threading.Lock()
    self.subscriptionThread = threading.Thread(target=self._processSubscription, name=f'SubscriptionThread', args=[self.subscription])
    self.subscriptionThread.start()

  def _reconnectHandler(self):
    while self.running.is_set():
      with self.reconnect:
        self.reconnect.wait()
      if not self.connectedEvent.is_set() and self.running.is_set():
        self.subscriptionThread.join()
        self.subscriberChannel = grpc.insecure_channel(f'{self.host}:{self.port}', options=self.channelOptions)
        self.subscriber = self.publisherStub(self.subscriberChannel)
        self.logger.debug(f'Reconnect attemp {self.host}:{self.port}')
        self.connect()

  def _block(self):
    if not self.connectedEvent.is_set() and self.running.is_set():
      self.connected = False
      self.subscriberChannel.close()

  def _processSubscription(self, subscription: _MultiThreadedRendezvous) -> None:
    '''! Processes incoming messages after subscription to a publisher server.
    If a callback method `processSubscription` was registered during object creation, it will be called every time a new message is received.
    This method blocks until the connection to the server is closed.
    Therefore, this method should run on its own thread.
    '''
    try:
      self.connectedEvent.clear()
      self.timer = threading.Timer(self.timeout, self._block)
      self.timer.start()
      for message in subscription:
        if (not self.connectedEvent.is_set()):
          self.logger.success(f'Connected: {self.host}:{self.port}')
          self.timer.cancel()
          self.connectedEvent.set()
        self.connected = self.connectedEvent.is_set()
        if self.callback is not None:
          self.callback(message)
    except grpc.RpcError as e:
      if e.code() == grpc.StatusCode.CANCELLED:
        if not self.running:
          self.logger.warning(f'Subscription cancelled: {e.details()}')
      else:
        self.logger.error(f'Subscription lost: {e}')

    if self.connectedEvent.is_set() and self.running.is_set():
      self.logger.warning(f'Server closed the connection: {self.host}:{self.port}, reconnecting...')
    self.connectedEvent.clear()
    self.connected = False
    with self.reconnect:
      self.reconnect.notify_all()

  def _subscribe(self, waitForReady=True, timeout=None) -> _MultiThreadedRendezvous:
    '''! Subscribes to the configured publisher.
    @param waitForReady If True this call will block until the publisher responds or timeout is exceeded. Defaults to True.
    @param timeout Amount of time to block if wait_for_ready is True in [s]. Defaults to None, implying wait for ever.
    '''
    subscription = self.subscriber.subscribe(pbBase.Subscribe(), wait_for_ready=waitForReady, timeout=timeout)
    return subscription

  def close(self):
    self.running.clear()
    self.timer.cancel()
    with self.reconnect:
      self.reconnect.notify_all()
    self.reconnectThread.join()
    self.subscriberChannel.close()
    self.subscriptionThread.join()


class Client():
  def __init__(self, name: str, subscriber: Subscriber | list[Subscriber] = None, requester: Requester = None):
    '''! Create a new Client.
      @param host The host where the server is running.
      @param processSubscription An optional callback function to process incoming server publisher messages.
    '''
    self.logger: Logger = Logger(f'{name}')
    if isinstance(subscriber, Subscriber):
      self.subscriber = subscriber
      if self.subscriber is not None:
        self.subscriber.setProcessSubscriptionCallback(self.processSubscription)
        self.logger.info(f'Connecting to server on {self.subscriber.host}:{self.subscriber.port}')
        self.subscriber.connect()
    elif isinstance(subscriber, list):
      self.subscriber = subscriber
      for s in self.subscriber:
        # FIXME somehow the subscriber should already know how to process the subscription
        # self.subscriber.setProcessSubscriptionCallback(self.processSubscription)
        self.logger.info(f'Connecting to server on {s.host}:{s.port}')
        s.connect()

    self.requester = requester
    if requester is not None:
      self.logger.info(f'Connecting to responder on {self.requester.host}:{self.requester.port}')
      requester.connect()

  def processSubscription(self, message: object):
    """Process the subscription of the subscriber
    Should be implemented in case the client has a subscriber

    :param object message: one of the contained objects in the streamed message
    """
    return

  def shutdown(self) -> None:
    '''! Stop the robot client, closes requester and subscriber channels.'''
    if isinstance(self.subscriber, Subscriber):
      self.subscriber.close()
    elif (isinstance(self.subscriber, list)):
      for s in self.subscriber:
        s.close()
    if self.requester is not None:
      self.requester.close()
    self.logger.info('Shutdown')
