import numpy as np


def rotate_points(points, r_matrix = np.array([[1, 0, 0],
                             [0, 0.81733806, 0.57615839],
                             [0, -0.57615839, 0.81733806]])):
    """
    Rotate a list of 3D points using a rotation matrix
    Default rotation matrix obtained from calibration is negative direction 120 degrees around the x-axis

    """
    r_point_list = []
    for p in points:
        # Make sure points has the correct shape
        if p.shape[0] != 3:
            raise ValueError("Input points must have shape (3, N)")

        # Apply the rotation transformation
        rotated_points = np.dot(r_matrix, p)

        r_point_list.append(rotated_points)

    return r_point_list