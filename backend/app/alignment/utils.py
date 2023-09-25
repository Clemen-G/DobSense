import math
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


def get_unit_vector(az, alt):
    """Converts alt-az angles to a unit vector

    Args:
        az: azimuth in degrees
        alt: altitude in degrees

    Returns:
        A (3, 1) unitary vector
    """
    return rot(Z, r(-az)) @ rot(Y, r(-alt)) @ np.array([1, 0, 0]).reshape([3, -1])


def get_taz_angles(vector):
    """Given a 3d vector, it returns its alt-az angles according to the
    following convention:
    - the vector corresponding to az-alt angle (0,0) is [1, 0, 0]
    - the vector corresponding to az-alt angle (0, 90) is [0, 1, 0]
    - the vector corresponding to az-alt angle (-90, 0) is [0, 0, 1]

    This function is the inverse of get_unit_vector(az, alt)
    Args:
        vector: a (3,) or (3, 1) np.array or list
    
    Returns:
        A (az, alt) tuple, with angles in degrees.
    """
    vector = np.squeeze(np.array(vector))
    # when v_1, v0 are positive we have negative azimuth
    az = -deg(math.atan2(vector[1], vector[0]))
    # returning a 0 <= <= 360 result (-180 <= atan <= 180)
    if az < 0:
        az = 360 + az
    
    alt = deg(math.atan2(vector[2],
                     math.sqrt(
                         math.pow(vector[0], 2) + math.pow(vector[1], 2))))
    return (az, alt)