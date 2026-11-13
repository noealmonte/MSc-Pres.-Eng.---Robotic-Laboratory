'''
Copyright (C) BFH roboticsLab
All rights reserved.
'''

from __future__ import annotations
import numpy as np
import rowan
from ch.bfh.roboticsLab import Base_pb2 as pbBase


class TransformationMatrix:
  '''
  This class implements a homogeneous transformation matrix.

  Usage example with robotClient:
    .. code-block:: python
      client = RobotClient('localhost')
      pose = client.getRobotPose()
      T_BT = TransformationMatrix.fromPose(pose)
  '''

  def __init__(self, transformationMatrix: np.ndarray = np.eye(4, dtype=float), tol=1e-9) -> None:
    '''
    Create a new homogeneous transformation matrix.

    :param np.ndarray transformationMatrix: A 4x4 matrix to initialize the TransformationMatrix, defaults to an identity matrix.
    '''
    T = transformationMatrix
    if T.shape != (4, 4):
        raise ValueError(f"Invalid shape {T.shape}, must be (4,4).")

    if not np.allclose(T[3, :], [0, 0, 0, 1], atol=tol):
        raise ValueError(f"Invalid bottom row {T[3, :]}, must be [0, 0, 0, 1].")

    R = T[:3, :3]

    if not np.allclose(R.T @ R, np.eye(3), atol=tol):
        raise ValueError("Rotation part is not orthonormal (R.T @ R != I).")

    det = np.linalg.det(R)
    if not np.isclose(det, 1.0, atol=tol):
        raise ValueError(f"Determinant of rotation is {det:.6f}, must be +1.")
    
    self.T = transformationMatrix
    
  @classmethod
  def fromCorrespondingPoints(cls, P_A:np.ndarray, P_B:np.ndarray, tol:float=1e-9) -> tuple[TransformationMatrix, float]:
    '''
    Compute the optimal rigid transform (rotation + translation) that aligns point set P_A to point set P_B using 
    the Kabsch algorithm [1]_.
    Assuming P_A are in the frame {A} and P_B are in the frame {B}, this constructor returns the TransformationMatrix object 
    $^B_AT$
    
    :param np.ndarray P_A: (N,3) array source points in frame {A}, minimum 3 non collinear points
    :param np.ndarray P_B: (N,3) array target points in frame {B}, minimum 3 non collinear points
    :param float tol: Numerical tolerance to check that the points are not collinear
    
    :return tuple[TransformationMatrix, float]: Transformation matrix objects from {A} to {B}, RMS error [same unit as P_A and P_B] (average Euclidean 
    distance between each transformed source point and its corresponding target point)
    
    References
    ----------
    .. [1] Lawrence J, Bernal J, Witzgall C.
           A Purely Algebraic Justification of the Kabsch-Umeyama Algorithm.
           J Res Natl Inst Stand Technol. 2019 Oct 9;124:1-6.
           doi:10.6028/jres.124.028. PMID:34877177; PMCID:PMC7340555.
    '''
    # Check inputs
    P_A = np.asarray(P_A, dtype=float)
    P_B = np.asarray(P_B, dtype=float)
    if P_A.shape != P_B.shape or P_A.shape[1] != 3:
        raise ValueError("P_A and P_B must be (N,3) arrays of the same shape.")
    N = P_A.shape[0]
    if N < 3:
        raise ValueError("At least 3 points are required for 3D rigid transform.")
    
    # Degeneracy check: ensure points are not collinear
    # Compute centered covariance
    X = P_A - P_A.mean(axis=0)
    rank = np.linalg.matrix_rank(X, tol=tol)
    if rank < 2:
        raise ValueError("Points are degenerate (collinear). Cannot compute unique 3D transform.")

    # --- Kabsch algorithm ---
    # Compute centroids
    mu_P:np.ndarray = P_A.mean(axis=0)
    mu_Q:np.ndarray = P_B.mean(axis=0)

    # Center the points by subtracting the centroids
    X = P_A - mu_P
    Y = P_B - mu_Q

    # Compute the covariance matrix
    H = X.T @ Y

    # Singular Value decomposition (SVD) to find the rotation that best aligns them (in least-squares sense).
    U, _, Vt = np.linalg.svd(H)
    V = Vt.T
    R = V @ U.T

    # Ensure proper rotation (no reflection)
    if np.linalg.det(R) < 0:
        V[:, -1] *= -1
        R = V @ U.T

    # Compute the optimal Translation after correcting the rotation
    t = mu_Q - R @ mu_P

    # Build homogeneous transform
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = t

    # Compute RMS error
    P_aligned = (R @ P_A.T).T + t
    rms = np.sqrt(np.mean(np.sum((P_B - P_aligned)**2, axis=1)))

    return cls(T), rms
    

  @classmethod
  def compose(cls, position: np.ndarray | list[float], orientation: np.ndarray | list[float]) -> TransformationMatrix:
    '''
    Creates a TransformationMatrix object from position and orientation arrays.

    :param np.ndarray | list[float] position: [x, y, z] {m}
    :param np.ndarray | list[float] orientation: quaternion [qw, qx, qy, qz]
    :return TransformationMatrix: class instance

    **Usage**
    .. code-block:: python
      T_B0 = TransformationMatrix.compose([1, 2, 3], [1, 0, 0, 0])
    '''
    # TODO Assert that position has only 3 elements or use only first 3 elements.
    position = np.reshape(position, (3, ))
    # TODO Assert that orientation has 4 elements.
    quaternion = rowan.normalize(q=orientation)
    rotMatrix = rowan.to_matrix(q=quaternion)
    tMatrix = np.eye(N=4, dtype=np.float64)
    tMatrix[:3, :3] = rotMatrix
    tMatrix[:3, -1] = position
    return cls(tMatrix)

  def decompose(self) -> tuple[np.ndarray, np.ndarray]:
    '''
    Retrieve the position and orientation components of this TransformationMatrix as numpy arrays.

    :return tuple[np.ndarray, np.ndarray]: position [x, y, z] {m}, orientation as quaternion [qw, qx, qy, qz]

    **Usage**
    .. code-block:: python
      T_B0 = TransformationMatrix.compose([1, 2, 3], [np.sqrt(0.5), np.sqrt(0.5), 0, 0])
      position, orientation = T_B0.decompose()
      >>> [1, 2, 3], [0.707, 0.707, 0, 0]
    '''
    position = np.reshape(self.T[:3, -1], (3,))
    rotMatrix = self.T[:3, :3]
    quaternion = rowan.normalize(rowan.from_matrix(rotMatrix))
    return position, quaternion

  def toArrayWithFixedAngles(self) -> np.ndarray:
    '''
    Retrieves the pose represented by this TransformationMatrix as an array containing the Cartesian position in the first 3 elements and a fixed-angle XYZ sequence in the last 3 elements.

    :return np.ndarray: [x, y, z, rx, ry, rz] {m, rad}

    **Usage**
    .. code-block:: python
      T_B0 = TransformationMatrix.compose([1, 2, 3], [np.sqrt(0.5), np.sqrt(0.5), 0, 0])
      print(T_B0.toArrayWithFixedAngles())
      >>> [1, 2, 3, 1.57, 0, 0]
    '''
    rotMatrix = self.T[:3, :3]
    quaternion = rowan.from_matrix(mat=rotMatrix)
    return np.concatenate([self.T[:3, -1], np.flip(rowan.to_euler(quaternion, 'zyx'))], None)

  def getOrientationAsFixedAngles(self) -> np.ndarray:
    '''
    Retrieves the orientation component of this TransformationMatrix as a fixed-angle XYZ sequence.

    :return np.ndarray: [rx, ry, rz] {rad}

    **Usage**
    .. code-block:: python
      T_B0 = TransformationMatrix.compose([1, 2, 3], [np.sqrt(0.5), np.sqrt(0.5), 0, 0])
      print(np.degrees(T_B0.getOrientationAsFixedAngles()))
      >>> [90, 0, 0]
    '''
    rotMatrix = self.T[:3, :3]
    quaternion = rowan.from_matrix(mat=rotMatrix)
    return np.flip(rowan.to_euler(q=quaternion, convention='zyx'))

  @classmethod
  def fromArrayWithFixedAngles(cls, pose: np.ndarray) -> TransformationMatrix:
    '''
    Creates a TransformationMatrix from a Cartesian array with fixed-angles XYZ sequence.

    :param np.ndarray pose: [x, y, z, rx, ry, rz] {m|rad}
    :return TransformationMatrix: class instance

    **Usage**
    .. code-block:: python
      T_B0 = TransformationMatrix.fromArrayWithFixedAngles([1, 2, 3, np.pi, 0, 0])
    '''
    # TODO Assert pose is size 3+4
    position = pose[:3]
    quaternion = rowan.from_euler(*np.flip(pose[3:]))
    rotMatrix = rowan.to_matrix(q=quaternion)
    tMatrix = np.eye(N=4, dtype=np.float64)
    tMatrix[:3, :3] = rotMatrix
    tMatrix[:3, -1] = position
    return cls(tMatrix)

  def _inverse(self) -> TransformationMatrix:
    '''
    Private method to invert a TransformationMatrix.
    Use operator `~`.
    See `__invert__`.

    :return TransformationMatrix: new TransformationMatrix object containing the inverted matrix
    '''
    R_inv = np.transpose(self.T[:3, :3])
    v_inv = -(np.linalg.matmul(R_inv, np.reshape(self.T[:3, -1], (3, 1))))
    T_inv = np.vstack((np.hstack((R_inv, v_inv)), [0, 0, 0, 1]))
    return TransformationMatrix(T_inv)

  def invert(self) -> TransformationMatrix:
    '''
    Invert this TransformationMatrix in place.

    :return TransformationMatrix: new TransformationMatrix object containing the inverted matrix
    '''
    return self._inverse()

  def transform(self, vector: np.ndarray | list[float]) -> np.ndarray:
    '''
    Applies this TransformationMatrix to the given vector representing a position.

    :param np.ndarray | list[float] vector: position [x, y, z] {m}
    :return np.ndarray: Transformed position [x, y, z] {m}

     **Usage**
    .. code-block:: python
      P_A = T_AB.transform(P_B)
    '''
    # TODO Assert vec size 3
    vector = np.array(vector)
    vector = np.reshape(np.append(vector, 1), (4, 1))
    return np.matmul(self.T, vector)[:3]

  ###  Python overload methods  ###
  # The class methods in this section implement Python operator and function overloads.

  def __mul__(self, other: TransformationMatrix) -> TransformationMatrix:
    '''
    Implements Python's '*' operator.
    Post-multiplies this TransformationMatrix with the given one.

    :param TransformationMatrix other: the other transformation matrix to be multiplied to the right of this one.
    :return TransformationMatrix: result of the calculation.

    **Usage**
    .. code-block:: python
      T_AC = T_AB * T_BC
    '''
    T = np.matmul(self.T, other.T)
    return TransformationMatrix(T)

  def __imul__(self, other: TransformationMatrix):
    '''
    Implements Python's '*=' operator.
    Post-multiply this TransformationMatrix with the given one in place, replacing its contents.

    :param TransformationMatrix other: the other transformation matrix to be multiplied to the right of this one.

    **Usage**
    .. code-block:: python
      T *= T_1
    '''
    self.transformationMatrix = np.matmul(self.T, other.T)

  def __truediv__(self, other: TransformationMatrix) -> TransformationMatrix:
    '''
    Implements Python's '/' operator.
    Post-multiply this TransformationMatrix with the inverse of the given one.

    :param TransformationMatrix other: the other transformation matrix to be inverted and then multiplied to the right of this one.
    :return TransformationMatrix: result of the calculation.

    **Usage**
    .. code-block:: python
      T_AC = T_AB / T_CB
    '''
    return self * other.invert()

  def __invert__(self) -> TransformationMatrix:
    '''
    Implements Python's '~' operator.
    Inverts this matrix and returns the result.

    :return TransformationMatrix: result of inverting this matrix.

    **Usage**
    .. code-block:: python
      T_AB = (~T_BA)
      T_AC = T_AB * (~T_CB)
    '''
    return self._inverse()

  def __eq__(self, other: TransformationMatrix) -> bool:
    '''
    Implements Python's '==' operator.
    Checks if the given TransfomationMatrix is equal to this one.
    The matrices will be equal if their individual elements are equal.

    :param TransformationMatrix other: second transformation
    :return bool: True if are equal, False otherwise
    '''
    return np.allclose(self.T, other.T)

  def __str__(self) -> str:
    '''
    Implements Python's '__str__' function.
    Creates a pretty string describing this object.
    '''
    try:
      position, orientation = self.pbDecompose()
      vec = np.round(self.toArrayWithFixedAngles(), decimals=4)
      positionStr = "Position: \n\tx: {x:.5f} \n\ty: {y:.5f} \n\tz: {z:.5f}\n".format(x=position.x, y=position.y, z=position.z)
      orientationStr = "Orientation: \n\tqw: {qw:.5f} \n\tqx: {qx:.5f} \n\tqy: {qy:.5f} \n\tqz: {qz:.5f}\n".format(
          qw=orientation.qw, qx=orientation.qx, qy=orientation.qy, qz=orientation.qz)
      fixedAngleVecStr = f"Fixed angle array: \n\tposition:{vec.tolist()[:3]} m\n\torientation: {np.round(np.degrees(vec.tolist()[3:]), decimals=2)} deg\n"

      s = [[str(e) for e in row] for row in self.T]
      lens = [max(map(len, col)) for col in zip(*s)]
      fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
      table = [fmt.format(*row) for row in s]
      tableStr = 'Matrix:\n' + '\n'.join(table)
      return positionStr + orientationStr + fixedAngleVecStr + tableStr
    except:
      s = [[str(e) for e in row] for row in self.T]
      lens = [max(map(len, col)) for col in zip(*s)]
      fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
      table = [fmt.format(*row) for row in s]
      tableStr = 'Matrix:\n' + '\n'.join(table)
      return tableStr

  ###  Protobuf conversion methods  ###
  # The class methods in this section implement utility functions to convert
  # TransformationMatrix objects and their data to protobuf objects for serialization.
  # see: ch.bfh.roboticsLab.Base_pb2

  @classmethod
  def fromPose(cls, pose: pbBase.Pose) -> TransformationMatrix:
    '''
    Creates a new Transformation matrix from a base.pb.pose pose object.

    :param pbBase.Pose pose: A pose object in protobuf base.Pose format.
    :raises RuntimeWarning: If the orientation component is not a valid quaternion.
    :return TransformationMatrix
    '''
    # TODO Could there be a better assertion to check the quaternion, e.g. using rowan?
    if pose.orientation.qw + pose.orientation.qx + pose.orientation.qy + pose.orientation.qz == 0:
      error = f'fromPose: invalid orientation {pose}'
      raise RuntimeWarning(error)
    position = np.reshape(
        [pose.position.x, pose.position.y, pose.position.z], (3, ))
    quaternion = rowan.normalize(
        [pose.orientation.qw, pose.orientation.qx, pose.orientation.qy, pose.orientation.qz])
    rotMatrix = rowan.to_matrix(quaternion)
    tMatrix = np.eye(4, dtype=np.float64)
    tMatrix[:3, :3] = rotMatrix
    tMatrix[:3, -1] = position
    return cls(tMatrix)

  def pose(self) -> pbBase.Pose:
    '''
    Creates a protobuf Pose object from this TransformationMatrix.

    :raises Exception: If converting the transformation matrix to protobuf object fails.
    :return pbBase.Pose: Protobuf Pose object

    **Usage**
    .. code-block:: python
      T_B0 = TransformationMatrix.compose([1, 2, 3], [1, 0, 0, 0])
      protoPose = T_B0.pose()
    '''
    try:
      rotMatrix = self.T[:3, :3]
      position = self.T[:3, -1]
      protoPosition = pbBase.Position(x=position[0], y=position[1], z=position[2])
      # TODO: Verify that this conversion works as expected
      # if not go to euler and then to quaternion
      quaternion = rowan.from_matrix(rotMatrix)
      protoQuaternion = pbBase.Quaternion(qw=quaternion[0], qx=quaternion[1], qy=quaternion[2], qz=quaternion[3])
      return pbBase.Pose(position=protoPosition, orientation=protoQuaternion)
    except Exception as e:
      raise Exception('Requester.pose: ', e)

  def position(self) -> pbBase.Position:
    '''
    Creates a protobuf Position object from the translation component of this TransformationMatrix.

    :return pbBase.Position: object
    '''
    position = self.T[:3, -1]
    return pbBase.Position(x=position[0], y=position[1], z=position[2])

  def orientation(self) -> pbBase.Quaternion:
    '''
    Creates a protobuf Quaternion object from the orientation component of this TransformationMatrix.

    :return pbBase.Quaternion: object
    '''
    rotMatrix = self.T[:3, :3]
    # TODO: Verify that this conversion works as expected
    # if not go to euler and then to quaternion
    quaternion = rowan.from_matrix(rotMatrix)
    return pbBase.Quaternion(qw=quaternion[0], qx=quaternion[1], qy=quaternion[2], qz=quaternion[3])

  def pbDecompose(self) -> tuple[pbBase.Position, pbBase.Quaternion]:
    '''
    Retrieve the Position and Quaternion (orientation) protobuf objects from this TransformationMatrix.

    :return tuple[pbBase.Position, pbBase.Quaternion]: protobuf objects
    '''
    return self.position(), self.orientation()

  @staticmethod
  def genPosition(position: np.ndarray | list[float]) -> pbBase.Position:
    '''
    Convert a list to a protobuf Position object

    :param np.ndarray | list[float] position: position as [x, y, z] in m
    :return pbBase.Position: Protobuf position object
    '''
    return pbBase.Position(x=position[0], y=position[1], z=position[2])

  @staticmethod
  def genOrientation(orientation: np.ndarray | list[float]) -> pbBase.Quaternion:
    '''
    Convert a list to a protobuf Quaternion

    :param np.ndarray | list[float] orientation: quaternion defined as [qw, qx, qy, qz]
    :return pbBase.Quaternion: Protobuf quaternion object
    '''
    quaternion = rowan.normalize(orientation)
    return pbBase.Quaternion(qw=quaternion[0], qx=quaternion[1], qy=quaternion[2], qz=quaternion[3])


#########################################
# Test & Example
#########################################
if __name__ == '__main__':
  T_B0 = TransformationMatrix()
  print(T_B0)
  pose = pbBase.Pose(position=pbBase.Position(x=0.1, y=0.2, z=0.3), orientation=pbBase.Quaternion(qw=1))

  T_01 = TransformationMatrix.fromPose(pose)
  print(T_01)

  T_B1 = T_B0 * T_01
  print(T_01)

  T_1B = ~T_01 * ~T_B0
  print(T_1B)

  print(T_1B == ~T_B1)
  print(T_1B == T_B1.invert())

  print(T_01.pose())
  P_0 = [0.1, 0.2, 0.3]
  P_B = T_B0.transform(P_0)
  print(P_B)

  T_10 = ~T_01
  print(T_01)
  print(T_01.invert())
  print(T_B1 == T_B0 / T_10)
  print(T_B1)
  print(T_B0 / T_10)
  print(T_B1.decompose())
  print(T_B1.orientation())

  T_FromFixed = TransformationMatrix.fromArrayWithFixedAngles([0, 0, 0, 0, 0, 0])
  print(T_FromFixed)
