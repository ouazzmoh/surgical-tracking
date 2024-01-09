import numpy as np

class StereoCalibration:
    def __init__(self, pair, rmse, mtx1, dist1, mtx2, dist2, R, T, E, F):
        self.pair = pair
        self.rmse = rmse
        self.mtx1 = mtx1
        self.dist1 = dist1
        self.mtx2 = mtx2
        self.dist2 = dist2
        self.R = R
        self.T = T
        self.E = E
        self.F = F
    
    def __str__(self):
        return f"T : {self.T} \n R : {self.R} "