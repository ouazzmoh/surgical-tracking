import cv2
import numpy as np
import datetime

from quadcam import QuadCam


# The goal of this script is to fill the calibration folder 

CALIB_DIR = "/home/cs/Desktop/stable/data/calibration_images/"


def solo_chess_cycle(index):
    
    """Should be ran to capture the calibration images
        index is the index of the camera
        Click "c" to capture the images
    """
    quadcam = QuadCam()
    quadcam.open_camera()

    print(".......To capture a picture click 'c'........")

    while cv2.waitKey(1) & 0xFF != ord('q'):
        quadcam.read()
        frame = quadcam.curr_frames[index]
        ret = False
        if cv2.waitKey(1) & 0xFF == ord('c'):
            print("Searching for chessBoard")
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, (4, 8), None)
            if ret == True:
                print("Found it")
                now = datetime.datetime.now()
                # Save the picture if border checking works
                path = CALIB_DIR +  f"solo/camera{index}/SoloCalib{index}__" + now.strftime("%Y-%m-%d_%H-%M-%S") + ".jpg"
                cv2.imwrite(path, frame)
                print("Image captured at " + path)
                cv2.drawChessboardCorners(frame, (4, 8), corners, ret)
            else:
                print("Didn't find it")
    
        cv2.imshow("cam", frame)
        if ret : 
            print('Click any button to continue')
            cv2.waitKey(0)
    quadcam.close_cameras()

    print("Calibration pictures stored for camera" + str(index))

    return 0

def stereo_chess_cycle(i, j):
    """
        i and j the indexes of the cameras to sterecalibrate
    """
    quadcam = QuadCam()
    quadcam.open_camera()

    while cv2.waitKey(1) & 0xFF != ord('q'):
        quadcam.read()
        retLeft, retRight = False, False
        frameLeft, frameRight = quadcam.curr_frames[i], quadcam.curr_frames[j]
        
        if cv2.waitKey(1) & 0xFF == ord('c'):

            print("Searching for chessBoards")
            grayLeft = cv2.cvtColor(frameLeft, cv2.COLOR_BGR2GRAY)
            retLeft, cornersLeft = cv2.findChessboardCorners(grayLeft, (4, 8), None)

            grayRight = cv2.cvtColor(frameRight, cv2.COLOR_BGR2GRAY)
            retRight, cornersRight = cv2.findChessboardCorners(grayRight, (4, 8), None)

            if retRight and retLeft :
                print("found it !")
                now = datetime.datetime.now()
                pathLeft = CALIB_DIR +  f"synched/camera{i}{j}/camera{i}/StereoCalib{i}__" + now.strftime("%Y-%m-%d_%H-%M-%S") + ".jpg"
                pathRight = CALIB_DIR +  f"synched/camera{i}{j}/camera{j}/StereoCalib{j}__" + now.strftime("%Y-%m-%d_%H-%M-%S") + ".jpg"
                cv2.imwrite(pathLeft, quadcam.curr_frames[i])
                cv2.imwrite(pathRight, quadcam.curr_frames[j])
                print("Images captured at " + pathLeft + "and" + pathRight)
                cv2.drawChessboardCorners(frameLeft, (4, 8), cornersLeft, retLeft)
                cv2.drawChessboardCorners(frameRight, (4, 8), cornersRight, retRight)
            else :
                print("Didn't find chess board in one the cameras")
            
        cv2.imshow("camLeft", frameLeft)
        cv2.imshow("camRight", frameRight)
        if retLeft and retRight:
             print("Press any button to continue")
             cv2.waitKey(0)
             
    quadcam.close_cameras()

    print("Calibration pictures stored for cameras" + str(i) + "and" + str(j))

    return 0


def main():
    
    print(".... Starting chessBoard capturing cycle for camera 0 ....")
    solo_chess_cycle(0)

    print(".... Starting chessBoard capturing cycle for camera 1 ....")
    solo_chess_cycle(1)

    print(".... Starting Synchronized chessBoard capturing cycle for camera pair {0, 1}")
    stereo_chess_cycle(0, 1)
    
    return 0



if __name__ == "__main__":
    main()