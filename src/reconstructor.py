import cv2
import numpy as np

class Reconstructor:

    def __init__(self):
        pass

    def triangulate(self, 
                    point_left, 
                    point_right, 
                    mtx_left,
                    mtx_right,
                    R0,
                    T0,
                    R1,
                    T1):
        """
        Takes as input two 2D points and returns the 
        triangulated 3D point
        """

        if point_left.shape != (2, ) or point_right.shape != (2, ):
            raise TypeError("The input points for triangulation are not in the right dimension (2, )")

        #TODO: potential issue here with R and T, wrong ref system
        P_left = mtx_left @ np.hstack((R0, T0)) # The left matrix is the reference
        P_right = mtx_right @ np.hstack((R1, T1))

        # The point is in homogenous coordinates
        point_4d = cv2.triangulatePoints(P_left, P_right, point_left, point_right)
        
        point_3d = point_4d[:3] / point_4d[3]

        return point_3d
