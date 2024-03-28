import cv2
import numpy as np
import matplotlib.pyplot as plt


from quadcam import QuadCam
from detector_green import DetectorGreen
from reconstructor import Reconstructor
from plot3d import Plot3DPoints
from transformations import rotate_points

R = np.array([[1, 0, 0],
             [0, 0.81733806, 0.57615839],
             [0, -0.57615839, 0.81733806]])
             
path = "/home/cs/Desktop/surgical-tracking/src/3d_point_coordinates.txt"


def save_coordinate(mean_points):
    with open(path, "w") as file:
        file.write(str(mean_points.tolist()))

def main():
    quadcam = QuadCam()
    quadcam.load_matlab_calibration()
    quadcam.open_camera()  # opens the cameras
    detector = DetectorGreen()  # instantiate the detector
    reconstructor = Reconstructor()  # instantiate the reconstructor
    scale = 1800 / quadcam.prop_w if quadcam.prop_w > 0 else 1
    points_3d_01 = []
    points_3d_02 = []
    points_3d_03 = []

    points_3d = []

    plotter = Plot3DPoints()

    while cv2.waitKey(1) != ord('q'):
        quadcam.read(scale)
        frame_with_green0, _, p0 = detector.detect(quadcam.curr_frames[0])
        frame_with_green1, _, p1 = detector.detect(quadcam.curr_frames[1])
        frame_with_green2, _, p2 = detector.detect(quadcam.curr_frames[2])
        frame_with_green3, _, p3 = detector.detect(quadcam.curr_frames[3])

        cv2.imshow("cam0", frame_with_green0)
        cv2.imshow("cam1", frame_with_green1)
        cv2.imshow("cam2", frame_with_green2)
        cv2.imshow("cam3", frame_with_green3)

        
        if p0 is not None and p1 is not None and p2 is not None and p3 is not None:
            d_p3d_01 = np.dot(R,
                              reconstructor.triangulate(p0, p1, quadcam.matrices[0], quadcam.matrices[1], np.eye(3),
                                            np.zeros((3, 1)), quadcam.stereo_calibrations[(0, 1)].R,
                                                        quadcam.stereo_calibrations[(0, 1)].T))
            d_p3d_02 = np.dot(R,
                              reconstructor.triangulate(p0, p2, quadcam.matrices[0], quadcam.matrices[2], np.eye(3),
                                            np.zeros((3, 1)), quadcam.stereo_calibrations[(0, 2)].R,
                                                        quadcam.stereo_calibrations[(0, 2)].T))
            d_p3d_03 = np.dot(R,
                              reconstructor.triangulate(p0, p3, quadcam.matrices[0], quadcam.matrices[3], np.eye(3),
                                                        np.zeros((3, 1)), quadcam.stereo_calibrations[(0, 3)].R,
                                                        quadcam.stereo_calibrations[(0, 3)].T))

            mean_points = (d_p3d_01 + d_p3d_02 + d_p3d_03) / 3
            
            save_coordinate(mean_points)

            points_3d.append(mean_points)

            points_3d_01.append(d_p3d_01)
            points_3d_02.append(d_p3d_02)
            points_3d_03.append(d_p3d_03)

    plotter.plot(points_3d, quadcam.stereo_calibrations[(0, 1)].T,
                 quadcam.stereo_calibrations[(0, 2)].T,
                 quadcam.stereo_calibrations[(0, 3)].T)


    quadcam.close_cameras()




if __name__ == "__main__":
    main()
