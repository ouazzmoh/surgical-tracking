import cv2 
import numpy as np
import matplotlib.pyplot as plt
import threading


from quadcam import QuadCam
from detector_red import DetectorRed
from detector_green import DetectorGreen
from reconstructor import Reconstructor

# CALIBRATION_PATH = "/home/cs/Desktop/surgical-tracking/data/stereo_calibration_data.npy"
# VIDEO_OUTPUT_DIR = "/home/cs/Desktop/surgical-tracking/outputs/"
#
# CALIB_DIR = "/Users/simo/surgical-tracking/data/calibration_images/"
# CALIB_DIR2 = "/Users/simo/surgical-tracking/dataset1/"
#
# CALIB_OUT = "/Users/simo/surgical-tracking/data/calib.pickle"
VIDEO_OUTPUT_DIR = '/Users/simo/surgical-tracking/video/'

def main():
    quadcam = QuadCam()

    quadcam.open_camera()  # opens the cameras


    scale = 1800 / quadcam.prop_w if quadcam.prop_w > 0 else 1

    quadcam.init_video_writers(VIDEO_OUTPUT_DIR)

    while cv2.waitKey(1) != ord('q'):
        quadcam.read(scale)
        frame0 = quadcam.curr_frames[0]
        frame1 = quadcam.curr_frames[1]
        quadcam.write(frame0, quadcam.outs[0])
        quadcam.write(frame1, quadcam.outs[1])

    quadcam.close_cameras()




if __name__ == "__main__":
    main()