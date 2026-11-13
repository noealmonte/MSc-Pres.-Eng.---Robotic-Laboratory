'''
MPE Advanced Robotics
Python interface to the Mecademic Meca500 robot.
@author gabriel.gruener@bfh.ch
'''

import socket, threading, time


class Meca500:
  '''
  This class allows to control a Meca500 robot with Python.

  Usage example:
  # Connect to robot
  meca = Meca500(ipAddress="192.168.0.100")

  # Activate
  meca.activate()
  # Home
  meca.home()

  # Set the robot's velocity [%]
  meca.setJointVelocity(velocity=25)

  # Move the robot to some joint positions [deg]
  theta = [0, 0, 0, 0, 0, 0]
  meca.moveJoints(theta=theta)
  # Waiting for the motion to end
  meca.waitIdle()

  ...

  # Disconnect from the robot controller
  meca.deactivate()
  del meca
  '''

  def __init__(self, ipAddress: str) -> None:
    '''
    Create a new Meca500 object.

    :param str ipAddress: IP Address of the robot to connect to.
    '''
    PORT = 10000  # The command TCP/IP port of the Meca500 server.
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
      self.socket.connect((ipAddress, PORT))
    except socket.error as error:
      raise error
    except Exception as e:
      raise e
    self.socket.settimeout(30.0)
    self.socket.recv(1024)

    self._eob_event = threading.Event()
    self._home_event = threading.Event()
    self._activate_event = threading.Event()
    self._deactivate_event = threading.Event()
    self._error_reset_event = threading.Event()
    self._clear_motion_event = threading.Event()
    self._motion_resumed_event = threading.Event()
    self._checkpoint_event = threading.Event()
    self._checkpoint_counter = 1

    self._error_event = threading.Event()
    self._last_error = ""

    self._response_event = threading.Event()
    self._last_response = ""

    self._is_connected = True
    self._listener_thread = threading.Thread(target=self._tcp_listener, daemon=True)
    self._listener_thread.start()

    self.reset()

  def disconnect(self) -> None:
    ''' Disconnecting from the robot.'''
    self._is_connected = False
    self.socket.shutdown(socket.SHUT_RDWR)
    self.socket.close()

  def _tcp_listener(self) -> None:
    '''
    Receive responds from the Meca500 and set the corresponding events
    '''
    self.socket.settimeout(0.5)

    while self._is_connected:
      try:
        data = self.socket.recv(1024).decode()
        if not data:
          continue

        for msg in data.split('\0'):
          if not msg:
            continue

          if "[2000]" in msg:
            self._activate_event.set()
          elif "[2002]" in msg:
            self._home_event.set()
          elif "[2004]" in msg:
            self._deactivate_event.set()
          elif "[2005]" in msg or "[2006]" in msg:
            self._error_reset_event.set()
          elif "[2043]" in msg:
            self._motion_resumed_event.set()
          elif "[2044]" in msg:
            self._clear_motion_event.set()
          elif "[3012]" in msg:
            self._eob_event.set()
          elif "[3030]" in msg:
            self._checkpoint_event.set()
          elif msg.startswith("[1")  or (msg.startswith("[3") and not msg.startswith("[30")):
            self._last_error = msg
            self._error_event.set()
            print(f"Error from robot: {self._last_error}")

          if msg.startswith("[1") or msg.startswith("[2") or (msg.startswith("[3") and not msg.startswith("[3000][Connected")):
            self._last_response=msg
            self._response_event.set()

      except socket.timeout:
        pass
      except Exception:
        if self._is_connected:
          self._error_event.set()
        break

  def _sendToRobot(self, command: str) -> None:
    '''
    Send the given command to the robot.

    :param str command: The string command to send to the robot, appending the necessary end of string ('\\0') to the command.
    '''
    b = bytes(command + "\0", 'utf-8')
    self.socket.sendall(b)

  def waitIdle(self, timeout: float = 60) -> None:
    '''
    Wait until all checkpoints are reached and the robot did reached the 'End of block'

    :param float timeout: Timeout for the function in seconds, defautlt 60 s.
    '''
    self._checkpoint_event.clear()
    self._eob_event.clear()
    self._error_event.clear()

    self._sendToRobot(f"SetCheckpoint({self._checkpoint_counter})")
    self._checkpoint_counter += 1

    start_time = time.monotonic()

    while not self._checkpoint_event.is_set():
        if self._error_event.is_set():
            raise RuntimeError(f"An error occurred while waiting for checkpoint: {self._last_error}")
        if (time.monotonic() - start_time) > timeout:
            raise TimeoutError("Timeout: Robot did not reach checkpoint.")
        self._checkpoint_event.wait(0.05)

    end_time = time.monotonic()
    remaining_timeout = timeout - (end_time - start_time)

    if remaining_timeout > 0:
        while not self._eob_event.is_set():
            if self._error_event.is_set():
                raise RuntimeError(f"An error occurred while waiting for End of Block: {self._last_error}")
            if (time.monotonic() - end_time) > remaining_timeout:
                raise TimeoutError("Timeout: Robot did not reach 'End of Block'.")
            self._eob_event.wait(0.05)

  def _waitHome(self) -> str:
    '''
    Wait untile the robot is homed.

    :return str: The robot's reply.
    '''
    self._home_event.clear()
    self._response_event.clear()
    self._error_event.clear()
    start_time = time.monotonic()

    while not self._home_event.is_set():
      if self._error_event.is_set():
        raise RuntimeError(f"An Error ocurred: {self._last_error}")
      if(time.monotonic() - start_time) > 40.0:
        raise TimeoutError("Timeout: Roboter did not reach 'Home'")
      self._home_event.wait(0.05)
    self._response_event.wait(5.0)
    self._response_event.clear()
    self._response_event.wait(5.0)
    return self._last_response

  def _waitActivated(self) -> str:
    '''
    Wait until the robot is activated.

    :return str: The robot's reply.
    '''
    self._error_event.clear()
    self._response_event.clear()
    start_time = time.monotonic()
    while not self._activate_event.is_set():
      if self._error_event.is_set():
        raise RuntimeError(f"An Error ocurred: {self._last_error}")
      if(time.monotonic() - start_time) > 30.0:
        raise TimeoutError("Timeout: Roboter did not reach 'Activate'")
      self._activate_event.wait(0.05)
    self._response_event.wait(5.0)
    return self._last_response

  def _waitDeactivated(self) -> str:
    '''
    Wait until the robot is deactivated.

    :return str: The robot's reply.
    '''
    self._error_event.clear()
    self._response_event.clear()
    start_time = time.monotonic()
    while not self._deactivate_event.is_set():
      if self._error_event.is_set():
        raise RuntimeError(f"An Error ocurred: {self._last_error}")
      if(time.monotonic() - start_time) > 10.0:
        raise TimeoutError("Timeout: Roboter did not reach 'Deactivate'")
      self._deactivate_event.wait(0.05)
    self._response_event.wait(5.0)
    return self._last_response

  def _waitClearMotion(self) -> str:
    '''
    Wait until the robot has cleared the motion.

    :return str: The robot's reply.
    '''
    self._error_event.clear()
    self._response_event.clear()
    start_time = time.monotonic()
    while not self._clear_motion_event.is_set():
      if self._error_event.is_set():
        raise RuntimeError(f"An Error ocurred: {self._last_error}")
      if(time.monotonic() - start_time) > 10.0:
        raise TimeoutError("Timeout: Roboter did not reach 'Clear Motion'")
      self._clear_motion_event.wait(0.05)
    self._response_event.wait(5.0)
    return self._last_response

  def _waitMotionResumed(self) -> str:
    '''
    Wait until the robot's movement is resumed.

    :return str: The robot's reply.
    '''
    self._error_event.clear()
    self._response_event.clear()
    start_time = time.monotonic()
    while not self._motion_resumed_event.is_set():
      if self._error_event.is_set():
        raise RuntimeError(f"An Error ocurred: {self._last_error}")
      if(time.monotonic() - start_time) > 10.0:
        raise TimeoutError("Timeout: Roboter did not reach 'Motion Resuming'")
      self._motion_resumed_event.wait(0.05)
    self._response_event.wait(5.0)
    return self._last_response

  def _waitResetError(self) -> str:
    '''
    Wait until all errors are reseted.

    :return str: The robot's reply.
    '''
    self._error_event.clear()
    self._response_event.clear()
    start_time = time.monotonic()
    while not self._error_reset_event.is_set():
      if self._error_event.is_set():
        raise RuntimeError(f"An Error ocurred: {self._last_error}")
      if(time.monotonic() - start_time) > 10.0:
        raise TimeoutError("Timeout: Roboter did not reach 'Reset Error'")
      self._error_reset_event.wait(0.05)
    self._response_event.wait(5.0)
    return self._last_response

  def getJoints(self) -> list[float]:
    '''
    Retrieve the current joint values.

    :return list[float]: Current joint values in [deg].
    '''
    self._response_event.clear()
    self._sendToRobot('GetRtJointPos')
    # Response: [2210][t, θ1, θ2, θ3, θ4, θ5, θ6]
    self._response_event.wait(timeout=5.0)
    if self._last_response.startswith('['):
      code_str = self._last_response.split(']')[0][1:]
      if code_str.isdigit():
        code = int(code_str)
        if (1000 <= code <= 1099):
          raise RuntimeError(f"Command Error: {self._last_response}")
    tokens = self._last_response.split(']')[1].split(',')[1:]
    joints = [float(x.strip()) for x in tokens]
    return joints

  def getPose(self) -> list[float]:
    '''
    Retrieve the current robotPose.

    :return list[float]: The current robot position and orientation as Euler angles [x, y, z, rx, ry, rz] in [mm|deg].
    '''
    self._response_event.clear()
    # Response: [2211][t, x, y, z, rx, ry, rz]
    self._sendToRobot('GetRtCartPos')
    self._response_event.wait(timeout=5.0)
    if self._last_response.startswith('['):
      code_str = self._last_response.split(']')[0][1:]
      if code_str.isdigit():
        code = int(code_str)
        if (1000 <= code <= 1099):
          raise RuntimeError(f"Command Error: {self._last_response}")
    tokens = self._last_response.split(']')[1].split(',')[1:]
    pose = [float(x.strip()) for x in tokens]

    return pose

  def activate(self) -> str:
    '''
    Activates the motors of the robot.

    :return str: The robot's reply.
    '''
    self._sendToRobot("ActivateRobot")
    return self._waitActivated()

  def deactivate(self) -> str:
    '''
    Stops and deactivates the motors of the robot.

    :return str: The robot's reply.
    '''
    self._sendToRobot("DeactivateRobot")
    return self._waitDeactivated()

  def reset(self) -> None:
    '''
    Checks the current state of the robot and resets and resumes motion if necessary
    '''
    self._response_event.clear()
    self._sendToRobot('GetStatusRobot')
    self._response_event.wait(timeout=5.0)
    try:
        # Extract part after the Code (e.g. [2007])
        status_str = self._last_response.split(']')[1].strip('[\0 \n\r')
        flags = [int(x.strip()) for x in status_str.split(',')]

        as_flag = flags[0] # Activation State
        es_flag = flags[3] # Error State
        pm_flag = flags[4] # Pause Motion
    except (IndexError, ValueError) as e:
        pass
        # raise RuntimeError(f"Not able to pars state: {self._last_response}") from e

    # Fix error state (es = 1)
    if es_flag == 1:
        print("Init: Error state detected. Send 'ResetError'...")
        self._sendToRobot('ResetError')
        self._waitResetError()

    # Fix paused-motion (pm = 1) only able when robot is activated
    if as_flag == 1:
        print("Init: motion paused. Send 'ResumeMotion'...")
        self._sendToRobot('ClearMotion')
        self._waitClearMotion()
        self._sendToRobot('ResumeMotion')
        self._waitMotionResumed()

  def home(self) -> str:
    '''
    Executes a homing procedure with the robot.

    :return str: The robot's reply.
    '''
    self._response_event.clear()
    self._sendToRobot("Home")
    return self._waitHome()

  def setJointVelocity(self, velocity: float) -> None:
    '''
    Sets the desired velocity of the joints in %.

    :param float velocity: The desired joint velocity in % [0..100].
    '''
    self._sendToRobot(f"SetJointVel({velocity:.3f})")

  def moveJoints(self, theta: list[float]) -> None:
    '''
    Moves the robot to the given joint angle configuration.

    :param list[float] theta: An array containing 6 values for the 6 robot joints in [deg].
    '''
    self._sendToRobot(f"MoveJoints({','.join(str(x) for x in theta)})")

  def moveJointsToPose(self, position: list[float], orientation: list[float]) -> None:
    '''
    Moves the robot to a given Cartesian position and orientation in joint space.

    :param list[float] position: The position of the TRF [x, y, z] in [mm].
    :param list[float] orientation: The orientation of the TRF as Euler angles [rx, ry, rz] in [deg].
    '''
    self._sendToRobot(f"MovePose({','.join(str(x) for x in position)}, {','.join(str(x) for x in orientation)})")

  def setToolOffset(self, position, orientation) -> None:
    '''
    Set the tool offset.

    :param _type_ position: Tool position offset as [x, y, z] in [mm]
    :param _type_ orientation: Tool orientation offset as Euler angle [rx, ry, rz] in [deg].
    '''
    self._sendToRobot(f"SetTRF({','.join(str(x) for x in position)}, {','.join(str(x) for x in orientation)})")

  def setCartesianLinearVelocity(self, velocity: float) -> None:
    '''
    Sets the desired velocity for linear motions [mm/s].

    :param float velocity: The desired Cartesian velocity for linear motions in [mm/s].
    '''
    velocity = min(1000, max(0.001, velocity))
    self._sendToRobot(f"SetCartLinVel({velocity:.3f})")

  def setCartesianAngularVelocity(self, angularVelocity: float) -> None:
    '''
    Sets the desired Cartesian angular velocity [deg/s].

    :param float angularVelocity: The desired Cartesian velocity for anfgular motions in [deg/s].
    '''
    angularVelocity = min(300, max(0.001, angularVelocity))
    self._sendToRobot(f"SetCartAngVel({angularVelocity:.3f})")

  def moveCartesian(self, position: list[float], orientation: list[float]) -> None:
    '''
    Moves the robot's tool reference frame (TRF) linearly to the given Cartesian position and orientation.
    :param list[float] position: Position of the TRF [x, y, z] in [m].
    :param list[float] orientation: Orientation of the tool as a Euler angle [rx, ry, rz] in [deg].
    '''
    self._sendToRobot(f"MoveLin({','.join(str(x) for x in position)}, {','.join(str(x) for x in orientation)})")

  def setBlending(self, blendingPercentage: int) -> None:
    '''
    Set the blending precentage between consecutive movements

    :param int blendingPercentage: precentag of blending, ranging from 0 (blending disabled) to 100.
    '''
    self._sendToRobot(f"SetBlending({blendingPercentage})")
