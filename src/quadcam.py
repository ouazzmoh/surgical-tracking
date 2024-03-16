import cv2
import numpy as np
import datetime
import glob
import pickle

from stereo_calibration import StereoCalibration

class QuadCam:

    """
        Model for arducam quadcamera
        
        Attributes:
            device_id : identifier in machine
            cvt_color : image color conversion encoding
            depth : 8-bit or 16-bit images
            cap : If camera is opened, instance of cv2.VideoCapture 
    """


    def __init__(self, 
                 device_id=0, 
                 cvt_color=48, 
                 depth=8,
                 calibrations=None,
                 prop_w = None,
                 prop_h = None,
                 outs = None):
        """
            The color encoding is BGRGR and the depth is by default 8
            because it is 8-bit images.
            It is advised not to pass the width and height
            as parameters, the proper ones will be decided later
            by default 5120 X 800
        """

        self.device_id = device_id
        self.cvt_color = cvt_color
        self.depth = depth
        self.calibrations = calibrations
        self.prop_w = prop_w
        self.prop_h = prop_h
        self.outs = outs # Video writer for each camera and the last one is for the grouped camera
        self.curr_frames  = None
        self.matrices = [None, None, None, None] # Camera matrices of the quadcam -> Only intrisic parameters determined by solo calibrate
        self.distortions = [None, None, None, None]
        self.stereo_calibrations = {}
        



    def open_camera(self):
        """
            Instantiate a capture instance and
        """
        try:
            self.cap = cv2.VideoCapture(self.device_id, cv2.CAP_V4L2) # CAP_V4L2 to use linux api

        except Exception as e:
            print(f"Could not open camera {self.device_id} : {e}")
            self.cap = None
            return
        # Set color conversion to rgb to False (It slows down FPS)
        self.cap.set(cv2.CAP_PROP_CONVERT_RGB, 0)

        self.prop_w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.prop_h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        print(f"""Camera opened : 
                   Default Resolution : {self.prop_w} x {self.prop_h}
                   Type : {self.depth}-bit images""")
        

    def read(self, scale=1):
        """
            Fetches the current frame from the quadcam and stores in the attribute curr_frames
            [frame_cam0, frame_cam1, frame_cam2, frame_cam3, global_frame]
        """
        if not self.cap or not self.prop_h or not self.prop_w:
            raise RuntimeError("Quadcam is not opened, use open_cameras() before calling this")
        
        w, h = self.prop_w, self.prop_h

        ret, frame = self.cap.read() # the returned frame is flat (1, wxh)
        frame = frame.reshape(int(h), int(w))

        frame = cv2.convertScaleAbs(frame, None, 
                                    256.0 / (1 << self.depth))
        frame = frame.astype(np.uint8)

        # After using the proper color encoding for the arducam cameras we convert it to rgb
        frame = cv2.cvtColor(cv2.cvtColor(frame, self.cvt_color), 
                             cv2.COLOR_BGR2RGB)
        # Resize 
        self.curr_frames = [frame[:, int(i * (w // 4)): int((i + 1) * (w // 4))] for i in range(4)]
        frame = cv2.resize(frame, (int(scale * w), int(scale * h)))
        self.curr_frames.append(frame)


    def init_video_writers(self, dir, scale=1, format="mp4v"):
        """
            Init the video writers stream, 
            [cam0, cam1, cam2, cam3, grouped] is the format of the attribute outs after calling this method
        """
        w, h = self.prop_w, self.prop_h
        extension = ".mp4" if format == "mp4v" else "" # todo:  check other CODEC formats
        fourcc = cv2.VideoWriter_fourcc(*format)
        now = datetime.datetime.now()
        paths = [dir + f"cam{i}__" + now.strftime("%Y-%m-%d_%H-%M-%S") + extension for i in range(4)]
        self.outs = [cv2.VideoWriter(path, fourcc,
                                20.0, (int(w//4), int(h))) for path in paths]   
        path_grouped = dir + "grouped" + now.strftime("%Y-%m-%d_%H-%M-%S") + extension
        self.outs.append(cv2.VideoWriter(path_grouped, fourcc, 20.0, (int(scale*w), int(scale*h))))
        print("Output streams initialized")


    def write(self, frame, out_stream):
        if not out_stream:
            raise RuntimeError("Output stream not initialized")
        out_stream.write(frame)


    def close_cameras(self):
        if self.cap:
            self.cap.release()
        if self.outs:
            for out in self.outs:
                if not out:
                    out.release()



    def solo_calibrate_cameras(self, calibration_dir, indexes = [0, 1], show_chess = False):
        """
            Find the intrisic parameters of the cameras with indexes in the argument
            indexes. By default calibrate the cameras 0 and 1

            calibration_dir the directory containing chess board images (9 x 5 / .7 cm), it should follow 
            the following hierarchy
            ./
                ./
                solo/
                    ./
                    camera0/...
                    camera1/...
                    camera2/...
                    camera3/...
                synched/
                    camera01/...
                    camera02/...
                    camera03/...
                    camera12/...
                    camera13/...
                    camera23/...
            Sets the attribute matrices
        """
        print("Calibrating for intrinsic parameters ...")
        for i in indexes:
            num_detected = 0
            images_folder = calibration_dir + f"solo/camera{i}/*"
            images_names = sorted(glob.glob(images_folder))
            images = []
            for imname in images_names:
                im = cv2.imread(imname, 1)
                images.append(im)
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            rows = 4 # number of rows 
            columns = 8 # number of columns in the chessboard
            world_size = .7

            objp = np.zeros((rows*columns, 3), np.float32)
            objp[:, :2] = np.mgrid[0:rows, 0:columns].T.reshape(-1, 2)
            objp = world_size * objp

            width = images[0].shape[1]
            height = images[0].shape[0]

            imgpoints = [] # Pixel coordinates of chess board
            objpoints = [] # coordinatres of chess board in world space

            for k, frame in enumerate(images):
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                

                ret, corners = cv2.findChessboardCorners(gray, (rows, columns), None)

                if ret == True:
                    num_detected += 1
                    conv_size = (11, 11)
                    corners = cv2.cornerSubPix(gray, corners, conv_size, (-1, -1), criteria)
                    if show_chess:
                        cv2.drawChessboardCorners(frame, (rows, columns), corners, ret)
                        cv2.imshow('imgChess', frame)
                        k = cv2.waitKey(500)
                        cv2.destroyAllWindows()

                    objpoints.append(objp)
                    imgpoints.append(corners)
                    
                
                # else :
                    # print(f"Chess board not found for picture : {images_names[k]}")
                
            if objpoints:
                rmse, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints,
                                                                    (width, height), None, None)

                # rmse score is related to the reprojuction error
                print(f"Detected {num_detected} out of {len(images)} chess boards for camera{i}")
                print(f"RMSE score for calibration of camera{i} is {rmse}")
                self.matrices[i] = mtx
                self.distortions[i] = dist

            else :
                print(f"Camera{i} could not be calibrated")
                

    def stereo_calibrate_cameras(self, calibration_dir, indexes = [(1, 0)], show_chess = False):
        """
            Find the extrinsic parameters of the cameras with indexes in the argument
            indexes. By default stereo calibrate the cameras 0 and 1
            the camera in the first position 0 in the default case is considered the reference frame
            ! Cameras should be solo calibrated first

            calibration_dir the directory containing chess board images (9 x 5 / .7 cm), it should follow 
            the following hierarchy
            indexes is a list of tuples representing the possible pairs, the first index is the left camera
            ./
                ./
                solo/
                    ./
                    camera0/...
                    camera1/...
                    camera2/...
                    camera3/...
                synched/
                    camera01/...
                    camera02/...
                    camera03/...
                    camera12/...
                    camera13/...
                    camera23/...
            Sets the attribute matrices
        """
        print("Calibrating for extrinsic parameters ...")
        for ij in indexes:
            i,j = ij[0], ij[1]
            if self.matrices[i] is None : raise AssertionError(f"Solo calibrate camera{i} first")
            if self.matrices[j] is None : raise AssertionError(f"Solo calibrate camera{j} first")

            # images_folder_left = calibration_dir + f"synched/camera{i}{j}/camera{i}/*"
            # images_folder_right = calibration_dir + f"synched/camera{i}{j}/camera{j}/*"

            # the first index is the left camera
            images_folder_left = calibration_dir + f"synched/camera{j}{i}/camera{i}/*"
            images_folder_right = calibration_dir + f"synched/camera{j}{i}/camera{j}/*"

            if not images_folder_left or not images_folder_right : raise RuntimeError("Could not load calibration images, make sure the path exists")

            images_names_left = sorted(glob.glob(images_folder_left))
            images_names_right = sorted(glob.glob(images_folder_right))
            images_left, images_right = [], []
            assert(len(images_names_right) == len(images_names_left))
            for k in range(len(images_names_left)):
                images_left.append(cv2.imread(images_names_left[k], 1))
                images_right.append(cv2.imread(images_names_right[k], 1))
            
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
            rows = 4 # number of rows 
            columns = 8 # number of columns in the chessboard
            world_size = .6

            objp = np.zeros((rows*columns, 3), np.float32)
            objp[:, :2] = np.mgrid[0:rows, 0:columns].T.reshape(-1, 2)
            objp = world_size * objp

            width = images_left[0].shape[1]
            height = images_left[0].shape[0]

            imgpoints_left = [] # Pixel coordinates of chess board
            imgpoints_right = []
            objpoints = [] # coordinatres of chess board in world space

            for k in range(len(images_left)):
                frame_left, frame_right = images_left[k], images_right[k]
                gray_left = cv2.cvtColor(frame_left, cv2.COLOR_BGR2GRAY)
                gray_right = cv2.cvtColor(frame_right, cv2.COLOR_BGR2GRAY)

                ret_left, corners_left = cv2.findChessboardCorners(gray_left, (rows, columns), None)
                ret_right, corners_right = cv2.findChessboardCorners(gray_right, (rows, columns), None)
                if ret_left == True and ret_right == True:
                    conv_size = (11, 11)

                    corners_left  = cv2.cornerSubPix(gray_left, corners_left, conv_size, (-1, -1), criteria)
                    corners_right  = cv2.cornerSubPix(gray_right, corners_right, conv_size, (-1, -1), criteria)

                    if show_chess:
                        cv2.drawChessboardCorners(frame_left, (rows, columns), corners_left, ret_left)
                        cv2.imshow('imgChess', frame_left)
                        cv2.drawChessboardCorners(frame_right, (rows, columns), corners_right, ret_right)
                        cv2.imshow('imgChess1', frame_right)
                        k = cv2.waitKey(500)
                        cv2.destroyAllWindows()

                    objpoints.append(objp)
                    imgpoints_left.append(corners_left)
                    imgpoints_right.append(corners_right)
                    
                
                else :
                    print(f"Chess board not found")
                
            if objpoints:
                # Solve only for the extrinsic parameters
                rmse, mtx1, dist1, mtx2, dist2, R, T, E, F = cv2.stereoCalibrate(objpoints, imgpoints_left, imgpoints_right,
                                                                    self.matrices[i], self.distortions[i],
                                                                    self.matrices[j], self.distortions[j],
                                                                    (width, height), criteria,
                                                                    flags = cv2.CALIB_FIX_INTRINSIC)

                # rmse score is related to the reprojuction error
                print(f"RMSE score for stereo calibration of pair camera{i}_{j} is {rmse}")
                
                calib = StereoCalibration((i,j), rmse, mtx1, dist1, mtx2, dist2, R, T, E, F)
                self.stereo_calibrations[(i, j)] = calib

            else :
                print(f"Camera{i} could not be calibrated")

    def full_calibrate_cameras(self, calibration_dir):
        self.solo_calibrate_cameras(calibration_dir, indexes=[0, 1, 2, 3])
        self.stereo_calibrate_cameras(calibration_dir, indexes=[(1, 0), (2, 1), (3, 2), (0, 3)])



    def save_calibration(self, path):
        """
            Save the calibration parameters to a file
        """
        with open(path, 'wb') as f:
            pickle.dump(self.stereo_calibrations, f)
        print("Calibration parameters saved")


    def load_calibration(self, path):
        """
            Load the calibration parameters from a file
        """
        with open(path, 'rb') as f:
            self.stereo_calibrations = pickle.load(f)
        print("Calibration parameters loaded")


    def load_matlab_calibration(self):
        """
            Load the calibration parameters from a matlab file

            This calibration was computed using matlab for stereo calibration

        """
        # Camera 0
        self.matrices[0] = np.array([[925.150083817515, 0, 649.570132897099],
                              [0, 923.175920622598, 408.253570992199],
                              [0, 0, 1]])
        self.distortions[0] = np.array([0.0265484763629214, -0.0474887177834878, 0, 0, 0])

        # Camera 1
        self.matrices[1] = np.array([[937.752950469242, 0, 648.5754302660850],
                              [0, 935.0085176908548, 417.2890951011200],
                              [0, 0, 1]])
        self.distortions[1] = np.array([0.0565389663830701, -0.0407582629327157, 0, 0, 0])

        # Camera 2
        self.matrices[2] = np.array([[9.180240059463720e+02, 0, 6.277720522905485e+02],
                              [0, 9.204316444213583e+02, 4.190038892235907e+02],
                              [0, 0, 1]])
        self.distortions[2] = np.array([0.0748385666898073, -0.128158374195814, 0, 0, 0])

        # Camera 3
        self.matrices[3] = np.array([[914.335833759638, 0, 630.292720701014],
                              [0, 912.545961130766, 412.160970970405],
                              [0, 0, 1]])
        self.distortions[3] = np.array([-0.00325637150773476, 0.0130107394069182, 0, 0, 0])

        # Stereo (0,1)
        R01 = np.array([[-0.00541120042425319, -0.821718425226070, -0.569868009765381],
                             [0.827234735343742, 0.316500160767844, -0.464230913312220],
                             [0.561830411735372, -0.473926658754197, 0.678041378214741]])
        T01 = np.array([[57.1694443257931],
                             [47.7830161026164],
                             [33.2653750415883]])
        stereo01 = StereoCalibration((0, 1), -1, self.matrices[0], self.distortions[0], self.matrices[1],
                                     self.distortions[1], R01, T01, 0, 0)


        # Stereo (0,2)
        R02 = np.array([[0.00794699837746728, 0.818037977742410, 0.575109304556879],
                             [-0.820076269615747, 0.334429392684904, -0.464361812944956],
                             [-0.572199053852686, -0.467943210528281, 0.673511243032050]])
        T02 = np.array([[-58.1990635190221], [46.774633773674410], [33.716830213033795]])
        stereo02 = StereoCalibration((0, 2), -1, self.matrices[0], self.distortions[0], self.matrices[2],
                                     self.distortions[2], R02, T02, 0, 0)

        # Stereo (0,3)
        R03 = np.array([[-0.999862702282291, 0.00373839076817029, 0.0161431415535822],
                             [-0.0164676879052049, -0.332457118625921, -0.942974591137008],
                             [0.00184169482034835, -0.943110963094701, 0.332473035674736]])
        T03 = np.array([[-1.12212719213900], [95.2909943777643], [67.1725791436523]])
        stereo03 = StereoCalibration((0, 3), -1, self.matrices[0], self.distortions[0], self.matrices[3],
                                     self.distortions[3], R03, T03, 0, 0)

        # Stereo extra
        Rextra = np.array([[1, 0, 0],
                             [0, 0.81733806, 0.57615839],
                             [0, -0.57615839, 0.81733806]])

        self.stereo_calibrations = {(0,1) : stereo01, (0,2) : stereo02, (0,3) : stereo03}



