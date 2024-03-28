from video_recorder import VideoRecorder
from calibration import Calibration
import numpy as np
main_path = "/home/cs/Desktop/last-version/Li/"

def load_calibration_data():
    calibration_data = np.load(main_path + "stereo_calibration_data.npy", allow_pickle=True).item()
    calibrations = []
    calibration_indexes = [12,13,14,23,24,34]
    for i in calibration_indexes:
        calibrations.append(Calibration(calibration_data, i))
    return calibrations

def main():
    calibrations = load_calibration_data()

    num_cameras = 4
    videos_directory = './scenes/'
    device = 0
    width = 1920
    height = 1080
    calibration_indexes = [12,13,14,23,24,34]

    recorder = VideoRecorder(num_cameras=num_cameras,
                             videos_directory=videos_directory,
                             device=device,
                             width=width,
                             height=height,
                             calibrations=calibrations,
                             calibration_indexes=calibration_indexes)
    recorder.main()

if __name__ == "__main__":
    main()































    
    
