import os
import cv2
import numpy as np

def load_calibration_images(folder):
    left_images = []
    right_images = []

    files = sorted(os.listdir(folder))

    for i, file in enumerate(files):
        img_path = os.path.join(folder, file)
        img = cv2.imread(img_path)

        if img is not None:
            if i < 15:
                left_images.append(img)
            else:
                right_images.append(img)

    return left_images, right_images

def stereo_calibration(left_images, right_images):
    # Prepare object points
    objp = np.zeros((6*9, 3), np.float32)
    objp[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)

    # Arrays to store object points and image points from all images
    objpoints = []  # 3D points in real-world space
    imgpoints_left = []  # 2D points in the image plane for the left camera
    imgpoints_right = []  # 2D points in the image plane for the right camera

    # Criteria for corner sub-pixel
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    for i in range(len(left_images)):
        print(f"Processing calibration for image pair {i + 1}...")

        # Convert images to grayscale
        gray_left = cv2.cvtColor(left_images[i], cv2.COLOR_BGR2GRAY)
        gray_right = cv2.cvtColor(right_images[i], cv2.COLOR_BGR2GRAY)

        # Find the chessboard corners
        ret_left, corners_left = cv2.findChessboardCorners(gray_left, (9, 6), None)
        ret_right, corners_right = cv2.findChessboardCorners(gray_right, (9, 6), None)

        if ret_left and ret_right:
            print("Chessboard corners found. Refining corners...")

            # Refine the corners using corner sub-pixel
            corners_left = cv2.cornerSubPix(gray_left, corners_left, (11, 11), (-1, -1), criteria)
            imgpoints_left.append(corners_left)

            corners_right = cv2.cornerSubPix(gray_right, corners_right, (11, 11), (-1, -1), criteria)
            imgpoints_right.append(corners_right)
            
            objpoints.append(objp)

            print("Corners refined and added to the calibration data.")
        else:
            print("Chessboard corners not found. Skipping this image pair.")

    if not imgpoints_left or not imgpoints_right:
        print("No valid image pairs found for calibration. Exiting...")
        return None

    # Calibrate the cameras
    print(f"Number of left images loaded: {len(left_images)}")
    print(f"Number of right images loaded: {len(right_images)}")


    print("Calibrating the left camera...")
    ret_left, camera_matrix_left, distortion_left, _, _ = cv2.calibrateCamera(objpoints, imgpoints_left, gray_left.shape[::-1], None, None)
    print(f"Left camera calibration {'successful' if ret_left else 'failed'}.")

    # Calibrate the right camera
    print("Calibrating the right camera...")
    ret_right, camera_matrix_right, distortion_right, _, _ = cv2.calibrateCamera(objpoints, imgpoints_right, gray_right.shape[::-1], None, None)
    print(f"Right camera calibration {'successful' if ret_right else 'failed'}.")

    # Stereo calibration
    flags = 0
    flags |= cv2.CALIB_FIX_INTRINSIC
    flags |= cv2.CALIB_USE_INTRINSIC_GUESS

    stereocalib_criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 100, 1e-5)

    print("Performing stereo calibration...")
    ret_stereo, _, _, _, _, R, T, E, F = cv2.stereoCalibrate(
        objpoints, imgpoints_left, imgpoints_right,
        camera_matrix_left, distortion_left,
        camera_matrix_right, distortion_right,
        gray_left.shape[::-1], criteria=stereocalib_criteria, flags=flags)

    print(f"Stereo calibration {'successful' if ret_stereo else 'failed'}.")

    return camera_matrix_left, distortion_left, camera_matrix_right, distortion_right, R, T, E, F

# Now you can use this function in your main script


def save_calibration_data(data, filename):
    np.save(filename, data)

# Main calibration process
calibration_data = {
    'camera_matrix_left': None,
    'distortion_left': None,
    'camera_matrix_right': None,
    'distortion_right': None,
    'R': None,
    'T': None,
    'E': None,
    'F': None
}

# Set the path to your image pairs
main_path = "/home/cs/Desktop/last-version/Li/"
image_pairs_path = main_path + 'pairs/'
save_path = main_path + 'stereo_calibration_data.npy'
save_path_txt = main_path + 'stereo_calibration_data.txt'

# For each stereo pair (camera1, camera2), (camera1, camera3), etc.
lst = [12,13,14,23,24,34]
for i in lst:
    folder_path = os.path.join(image_pairs_path, f'camera{i}')
    left_images, right_images = load_calibration_images(folder_path)

    # Perform stereo calibration
    calibration_result = stereo_calibration(left_images, right_images)

    # Update calibration data
    calibration_data[f'camera_matrix_left{i}'] = calibration_result[0]
    calibration_data[f'distortion_left{i}'] = calibration_result[1]
    calibration_data[f'camera_matrix_right{i}'] = calibration_result[2]
    calibration_data[f'distortion_right{i}'] = calibration_result[3]
    calibration_data[f'R{i}'] = calibration_result[4]
    calibration_data[f'T{i}'] = calibration_result[5]
    calibration_data[f'E{i}'] = calibration_result[6]
    calibration_data[f'F{i}'] = calibration_result[7]

# Save calibration data

np.save(save_path, calibration_data)
with open(save_path_txt, 'w') as txt_file:
    for key, value in calibration_data.items():
        txt_file.write(f"{key}:\n{value}\n\n")
            


