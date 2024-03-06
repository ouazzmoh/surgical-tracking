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
        return f"T : {self.T} \n R : {self.R}"

    def __repr__(self):
        return (f"mtx1 : {self.mtx1} \n mtx2 : {self.mtx2} \n dist1 : {self.dist1} "
                f"\n dist2 : {self.dist2} \n R : {self.R} \n "
                f"T : {self.T} \n E : {self.E} \n F : {self.F} \n "
                f"RMSE : {self.rmse} \n")