from math import pi
import numpy as np
from scipy.spatial.transform import Rotation as R

Origin = [0.0, 0, 0]
X = [1.0, 0, 0]
Y = [0, 1.0, 0]
Z = [0, 0, 1.0]


def norm(np_matrix):
    return np.linalg.norm(np_matrix, ord='fro')


def ppp(arr):
    print(np.round(arr.reshape(3, 3), 3))


def rot(axis, angle):
    """Generates the matrix for a rotation about an axis

    Arguments:
        axis -- rotation axis.
        angle -- rotation angle in radians.
        Right hand convention counterclockwise

    Returns:
        A 3x3 np.array
    """
    unit_axis = np.array(axis)
    unit_axis /= np.linalg.norm(unit_axis, 2)
    return np.array(R.from_rotvec(angle * np.array(axis)).as_matrix())


def r(deg):
    """Converts an angle deg -> radians

    Arguments:
        deg -- Angle in degree

    Returns:
        angle in radians
    """
    return 2 * pi * deg/360

def deg(rad):
    """Converts an angle radians -> deg

    Arguments:
        deg -- Angle in radians

    Returns:
        angle in degree
    """
    return 180 * rad / pi