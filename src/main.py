import cv2 
import numpy as np
import matplotlib.pyplot as plt


from quadcam import QuadCam
from detector_red import DetectorRed
from detector_green import DetectorGreen
from reconstructor import Reconstructor

CALIBRATION_PATH = "/home/cs/Desktop/surgical-tracking/data/stereo_calibration_data.npy"
VIDEO_OUTPUT_DIR = "/home/cs/Desktop/surgical-tracking/outputs/"

CALIB_DIR = "/Users/simo/surgical-tracking/data/calibration_images/"
CALIB_DIR2 = "/Users/simo/surgical-tracking/dataset1/"

CALIB_OUT = "/Users/simo/surgical-tracking/data/calib.pickle"


def main():
    quadcam = QuadCam()
    # quadcam.solo_calibrate_cameras(CALIB_DIR, indexes=[0, 1])
    # quadcam.stereo_calibrate_cameras(CALIB_DIR, indexes=[(1, 0)])

    # print(quadcam.stereo_calibrations)

    # quadcam.save_calibration(CALIB_OUT)

    quadcam.load_calibration(CALIB_OUT)

    print(quadcam.stereo_calibrations)













# def detect_red_green():
#     quadcam = QuadCam()
#     quadcam.open_camera()
#     # quadcam.calibrate_cameras(CALIBRATION_PATH)
#
#     scale = 1800 / quadcam.prop_w
#
#     detector = DetectorRed()
#     detector_green = DetectorGreen()
#
#
#     while cv2.waitKey(1) != ord('q'):
#         quadcam.read(scale)
#
#         frame_with_red, _, _ = detector.detect(quadcam.curr_frames[0])
#         frame_with_green, _, _ = detector_green.detect(quadcam.curr_frames[0])
#
#         cv2.imshow(f"ArducamRed{0}", quadcam.curr_frames[0])
#
#
#     quadcam.close_cameras()
#
#     return 0
#
# def check_detect_chess():
#     quadcam = QuadCam()
#     quadcam.open_camera()
#     reconstructor = Reconstructor()
#
#     while cv2.waitKey(1) != ord('q'):
#         quadcam.read()
#         frame = quadcam.curr_frames[0]
#         if cv2.waitKey(1) == ord('f'):
#             print("Searching for chessBoard")
#             gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#             ret, corners = cv2.findChessboardCorners(gray, (4, 8), None)
#             if ret == True:
#                 print("Found it")
#                 cv2.drawChessboardCorners(frame, (4, 8), corners, ret)
#                 cv2.imwrite("./chess.jpg", frame)
#             else:
#                 print("Didn't find it")
#
#         cv2.imshow("chess?", frame)
#         if ret == True:
#             cv2.waitKey(0)
#
#
#     quadcam.close_cameras()
#
#     return 0
#
#
#
# def main():
#
#     quadcam = QuadCam()
#     quadcam.open_camera()
#
#     quadcam.solo_calibrate_cameras(CALIB_DIR, indexes = [0, 1])
#
#     quadcam.stereo_calibrate_cameras(CALIB_DIR, indexes = [(1, 0)]) # We pass (1, 0) in this order because the
#
#
#     print(quadcam.stereo_calibrations[(1,0)])
#
#     scale = 1800 / quadcam.prop_w
#
#
#     detector = DetectorRed()
#     detector_green = DetectorGreen()
#
#     reconstructor = Reconstructor()
#     points_3d = []
#     points_3d_green = []
#
#     while cv2.waitKey(1) != ord('q'):
#         quadcam.read()
#
#         frame_with_red0, _, p0 = detector.detect(quadcam.curr_frames[0])
#         frame_with_red1, _, p1 = detector.detect(quadcam.curr_frames[1])
#
#         frame_with_red_green0, _, p0_green = detector_green.detect(frame_with_red0)
#         frame_with_red_green1, _, p1_green = detector_green.detect(frame_with_red1)
#
#         cv2.imshow("left", frame_with_red_green0)
#         cv2.imshow("right", frame_with_red_green1)
#
#
#
#
#         if p0 is not None and p1 is not None:
#             p3D = reconstructor.triangulate(p1, p0, quadcam.matrices[1], quadcam.matrices[0],
#                                             quadcam.stereo_calibrations[(1, 0)])
#             print(p3D)
#             points_3d.append(p3D)
#
#         if p0_green is not None and p1_green is not None:
#             p3D_green = reconstructor.triangulate(p1_green, p0_green, quadcam.matrices[1], quadcam.matrices[0],
#                                             quadcam.stereo_calibrations[(1, 0)])
#             print("Green")
#             print(p3D_green)
#             points_3d_green.append(p3D_green)
#
#
#     quadcam.close_cameras()
#     cv2.destroyAllWindows()
#     print(points_3d)
#
#     if points_3d and points_3d_green:
#             fig = plt.figure()
#             ax = fig.add_subplot(111, projection='3d')
#
#             x, y, z = [pt[0] for pt in points_3d], [pt[1] for pt in points_3d], [pt[2] for pt in points_3d],
#
#             xg, yg, zg = [pt[0] for pt in points_3d_green], [pt[1] for pt in points_3d_green], [pt[2] for pt in points_3d_green],
#             ax.scatter(x[0], y[0], z[0], color='red')
#             ax.scatter(x[1:-1], y[1:-1], z[1:-1], color='red')
#             ax.scatter(x[-1], y[-1], z[-1], color='blue')
#
#             ax.scatter(xg[0], yg[0], zg[0], color='green')
#             ax.scatter(xg[1:-1], yg[1:-1], zg[1:-1], color='green')
#             ax.scatter(xg[-1], yg[-1], zg[-1], color='blue')
#
#             ax.set_ylim([0, 30])
#             ax.set_xlim([0, 30])
#             ax.set_zlim([0, 30])
#
#             plt.savefig("triangulated_trajectory.png")
#             plt.show()
#
#     return 0



if __name__ == "__main__":
    main()