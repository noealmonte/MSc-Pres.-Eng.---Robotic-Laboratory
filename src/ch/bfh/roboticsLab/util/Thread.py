'''
Copyright (C) BFH roboticsLab
All rights reserved.
'''

import threading
import time
from typing import final
from abc import ABC, abstractmethod


class Thread(ABC):
  '''
  This class implements an abstract base class for classes that require a private thread.
  Implementing classes must implement the abstract method `_run()`.
  Method `_waitForNextPeriod()` will sleep the necessary time to maintain the execution period
  and return `True` or `False` depending on whether the thread should be stopped.

  Usage:
  .. code-block:: python
    class MyThread(Thread):

      def __init__(self, period:float) -> None:
        super().__init__(period, 'MyThread')

      def _run(self) -> None:
        counter = 0
        while (self._waitForNextPeriod()):
          counter += 1
          print(f'Counter: {counter}')
        print('Done')

    thread = MyThread(period=0.1)
    thread.start()
    time.sleep(10)
    thread.stop()
  '''

  def __init__(self, period: float, name: str = None) -> None:
    '''
    Creates a new Thread object with the given period and name.

    :param float period: Execution period of the thread in [s].
    :param str name: Name of the thread, defaults to None.
    '''
    self._period = period
    self._name = name
    self._thread: threading.Thread = None
    self._keepRunning = False

  def __del__(self) -> None:
    '''
    Destroys this thread, calling `stop()` first.
    '''
    self.stop()

  @final
  def start(self) -> None:
    '''
    Starts this thread.
    '''
    if not self.isRunning():
      self._thread = threading.Thread(target=self._run, name=self._name)
      self._keepRunning = True
      self._timeLoopStart = time.time()
      self._executionPeriod = self._period
      self._thread.start()

  @final
  def stop(self) -> None:
    '''
    Stops this thread.
    '''
    if self.isRunning():
      self._keepRunning = False
      self._thread.join()
      self._thread = None

  @final
  def isRunning(self) -> bool:
    '''
    Returns the running state of this thread.

    :return bool: `True` if the thread is running, `False` otherwise.
    '''
    return self._thread is not None

  @final
  def _waitForNextPeriod(self) -> bool:
    '''
    Blocks this thread for the rest of the duration of one period.

    :return bool: `False` if `stop()` was called; `True` otherwise.
    '''
    waitTime = self._period - (time.time() - self._timeLoopStart)
    if waitTime > 0:
      time.sleep(waitTime)
      self._executionPeriod = self._period
    else:
      self._executionPeriod = self._period + waitTime
    self._timeLoopStart = time.time()
    return self._keepRunning

  @final
  def getCyclePeriod(self) -> float:
    '''
    Returns the "exact" time period between different cycles.

    :return float: The last execution period in [s].
    '''
    return self._executionPeriod

  @abstractmethod
  def _run(self) -> None:
    '''
    Performs the work of the thread.
    This method will be called from `start()` and the thread will run until this method returns.
    Implementing class that run in a loop shall call `_waitForNextPeriod()` to execute the loop in the requested period
    and shall respect the return value to stop the loop.
    '''
    pass


# Unit tests
if __name__ == '__main__':
  import Logger

  class MyThread(Thread):
    def __init__(self) -> None:
      super().__init__(period=0.01, name='Test 1')
      self.times = []

    def _run(self):
      self.times.append(time.time())
      while self._waitForNextPeriod():
        self.times.append(time.time())

  def test1() -> bool:
    testLogger = Logger.Logger('Thread Test 1')
    myThread = MyThread()
    testLogger.info('test1 start')
    myThread.start()
    time.sleep(0.1)
    myThread.stop()
    testLogger.info(f'test1 stop: times={[b - a for a, b in zip(myThread.times[:-1], myThread.times[1:])]}')
    return True

  test1()
