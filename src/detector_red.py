import cv2
import numpy as np


class DetectorRed:
    
    def __init__(self, lower_red = np.array([0, 100, 100]), upper_red = np.array([10, 255, 255])):
        self.lower_red = lower_red
        self.upper_red = upper_red

    def detect(self, frame):
        # Convert the frame from BGR to HSV color space
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create a mask for the red color
        red_mask = cv2.inRange(hsv_frame, self.lower_red, self.upper_red)

        # Find contours in the red mask
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw contours on the original frame
        cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)

        # Get the coordinates of the centers of the detected red contours
        red_centers = []
        for contour in contours:
            # Calculate the center of the contour
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                red_centers.append((cX, cY))
                # Draw a small circle at the center
                cv2.circle(frame, (cX, cY), 5, (255, 255, 255), -1)
        red_point = None
        if red_centers:
            red_centers = np.array(red_centers)
            red_point = np.mean(red_centers, axis=0)
            cv2.circle(frame, (int(red_point[0]), int(red_point[1])), 20, (255, 0, 0), -1)
        return frame, red_centers, red_point