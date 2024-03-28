import numpy as np

class Calibration:
    def __init__(self, calibration_data, i=14):
        self.cam_mats_left = calibration_data[f'camera_matrix_left{i}']
        self.dist_coeffs_left = calibration_data[f'distortion_left{i}']
        self.cam_mats_right = calibration_data[f'camera_matrix_right{i}']
        self.dist_coeffs_right = calibration_data[f'distortion_right{i}']
        self.R = calibration_data[f'R{i}']
        self.T = calibration_data[f'T{i}']
        self.E = calibration_data[f'E{i}']
        self.F = calibration_data[f'F{i}']
