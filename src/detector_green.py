import cv2
import numpy as np


class DetectorGreen:
    
    def __init__(self, lower_green = np.array([40, 90, 20]), upper_green = np.array([50, 255, 255])):
        self.lower_green = lower_green
        self.upper_green = upper_green

    def detect(self, frame):
        # Convert the frame from BGR to HSV color space
        # TODO : Check the encoding with red
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV) # Convert to from RGB when green 

        # Create a mask for the green color
        green_mask = cv2.inRange(hsv_frame, self.lower_green, self.upper_green)

        # Find contours in the green mask
        contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw contours on the original frame
        cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)

        # Get the coordinates of the centers of the detected green contours
        green_centers = []
        for contour in contours:
            # Calculate the center of the contour
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                green_centers.append((cX, cY))
                # Draw a small circle at the center
                cv2.circle(frame, (cX, cY), 5, (255, 255, 255), -1)
        green_point = None
        if green_centers:
            green_centers = np.array(green_centers)
            green_point = np.mean(green_centers, axis=0)
            cv2.circle(frame, (int(green_point[0]), int(green_point[1])), 20, (255, 0, 0), -1)
        return frame, green_centers, green_point