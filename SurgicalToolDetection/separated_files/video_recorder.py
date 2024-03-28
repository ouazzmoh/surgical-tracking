import cv2
import json
import argparse
from arducam_camera import MyCamera
import numpy as np
from point_detector import PointDetector
from calibration import Calibration
from real_time_3d_plotter import RealTime3DPlotter
import threading
from queue import Queue
import tkinter as tk

class VideoRecorder:
    def __init__(self, num_cameras, videos_directory='./scenes/', device=0, width=1920, height=1080, calibrations=None,calibration_indexes=[]):
        self.num_cameras = num_cameras
        self.videos_directory = videos_directory
        self.device = device
        self.width = width
        self.height = height
        self.point_detector = PointDetector()
        self.calibrations = calibrations
        self.calibration_indexes = calibration_indexes

    def write_camera_params(self, fmt, filename):
        result = json.dumps(fmt, sort_keys=True, indent=4, separators=(',', ':'))
        fName = filename.replace('.mp4', '_params.txt')
        with open(str(fName), 'w') as f:
            f.write(result)

    def parse_cmdline(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-d', '--device', default=0, type=int, nargs='?',
                            help='/dev/videoX default is 0')
        parser.add_argument('--width', type=lambda x: int(x, 0), default=-1,
                            help="set width of image")
        parser.add_argument('--height', type=lambda x: int(x, 0), default=-1,
                            help="set height of image")

        args = parser.parse_args()
        return args

    def open_camera(self):
        camera = MyCamera()
        print("Open camera...")
        camera.open_camera(self.device, self.width, self.height)
        (width, height) = camera.get_framesize()
        print(f"Current resolution: {width}x{height}")
        return camera, width, height

    def initialize_video_writers(self, fmt, scale):
        image_width = int(fmt['width'] * scale)
        image_height = int(fmt['height'] * scale)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writers = [
            cv2.VideoWriter(self.videos_directory + f'camera_{i}_recording.mp4', fourcc, 20.0, (image_width // self.num_cameras, image_height))
            for i in range(self.num_cameras)
        ]

        return video_writers

    def normalize_3d_point(self, point):
        point = np.array(point)
        norm = np.linalg.norm(point)
        if norm != 0:
            normalized_point = point / norm
            return normalized_point
        else:
            print("Cannot normalize a zero vector.")
            return None

    def triangulate_points(self, point_left, point_right, calibration):
        if point_left.shape == (2, ) and point_right.shape == (2, ):
            print("Shapes are correct for triangulation.")
            P_left = calibration.cam_mats_left @ np.hstack((calibration.R, calibration.T))
            P_right = calibration.cam_mats_right @ np.hstack((calibration.R, calibration.T))
            print(f"TRY triangulation: P_left :{P_left.shape}, P_right = {P_right.shape},point_left = {point_left.shape},point_right = {point_right.shape}")
            try:
                point_4d = cv2.triangulatePoints(P_left, P_right, point_left, point_right)
                print(f"Triangulated 4D point: {point_4d}")
                point_3d = point_4d[:3] / point_4d[3]
                print(f"Triangulated 3D point: {point_3d}")
                return point_3d
            except Exception as e:
                print(f"Error during triangulation: {e}")
                return None
        else:
            print("Incorrect shape of input points for triangulation.")
            return None
    @staticmethod
    def return_cam_indexes(num):
        left = num//10-1
        right = num%10-1
        return left,right

    def capture_and_write_frames(self, camera, video_writers, image_width, image_height, point_3d_queue):
        
        while cv2.waitKey(1) != ord('q'):
            triangulation_results = []
            print("here")
            print(self.calibrations)
            for index, value in enumerate(self.calibrations):
                num = self.calibration_indexes[index]
                camera_left_index,camera_right_index = self.return_cam_indexes(num)
                frame = camera.get_frame()
                frame = cv2.resize(frame, (image_width, image_height))

                frames_split = [frame[:, i * (image_width // self.num_cameras): (i + 1) * (image_width // self.num_cameras)] for i in range(self.num_cameras)]

                print(f"Left Camera Index: {camera_left_index}, Write Index: {camera_right_index}")

                frame_left, red_points_left = self.point_detector.detect_red_objects(frames_split[camera_left_index])
                frame_right, red_points_right = self.point_detector.detect_red_objects(frames_split[camera_right_index])

                cv2.imshow(f"Arducam {camera_left_index}", frame_left)
                cv2.imshow(f"Arducam {camera_right_index}", frame_right)

                red_center_left = self.point_detector.get_mean_of_points(red_points_left)
                red_points_right = self.point_detector.get_mean_of_points(red_points_right)

                if red_center_left and red_points_right:
                    print(f"red_center_left: {red_center_left}, red_center_right: {red_points_right}")
                    point_3d = self.triangulate_points(np.array(red_center_left), np.array(red_points_right), self.calibrations[index])
                    print(f"3D Point {camera_left_index + 1}-{camera_right_index + 1}: {point_3d}")

                    if np.any(point_3d):
                        point_3d_queue.put(point_3d)
                        triangulation_results.append(point_3d)
                else:
                    print("Not enough points for triangulation.")
             
            if triangulation_results:
                mean_point = np.mean(triangulation_results, axis=0)
                print(f"Mean of triangulation results: {mean_point}")
            else:
                print("The list is empty.")     
    

    def close_camera_and_release_writers(self, camera, video_writers):
        camera.close_camera()

        for writer in video_writers:
            writer.release()

        print("Close camera...")


    def record_video(self, camera, fmt, scale, point_3d_queue):
        try:
            print("here")
            video_writers = self.initialize_video_writers(fmt, scale)
            self.capture_and_write_frames(camera, video_writers, int(fmt['width'] * scale), int(fmt['height'] * scale), point_3d_queue)
            self.close_camera_and_release_writers(camera, video_writers)
        except Exception as e:
            print(e)
            
    def main(self):
        args = self.parse_cmdline()

        try:
            camera, width, height = self.open_camera()

            fmt = {
                'device': args.device,
                'width': width,
                'height': height,
            }

            scale = 1280.0 / fmt['width']
            fmt['scale'] = scale

            # Create a queue for communication between the capture and plotting threads
            point_3d_queue = Queue()
            
            # Create an instance of RealTime3DPlotter
            #plotter = RealTime3DPlotter(point_3d_queue)

            # Start the video recording thread
            # video_recording_thread = threading.Thread(target=self.record_video, args=(camera, fmt, scale, point_3d_queue), daemon=True)
            # video_recording_thread.start()
            
            video_writers = self.initialize_video_writers(fmt, scale)
            self.capture_and_write_frames(camera, video_writers, int(fmt['width'] * scale), int(fmt['height'] * scale), point_3d_queue)
            self.close_camera_and_release_writers(camera, video_writers)
            
            #  # Wait for the plotting thread to finish (optional)
            # video_recording_thread.join()
        
            

            

        except Exception as e:
            print(e)

if __name__ == "__main__":
    VideoRecorder().main()
