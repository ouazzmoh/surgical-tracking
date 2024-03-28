import cv2 
import numpy as np
import matplotlib.pyplot as plt


from quadcam import QuadCam
from detector_green import DetectorGreen
from detector_red import DetectorRed
from reconstructor import Reconstructor
from plot3d import Plot3DPoints
from transformations import rotate_points

import subprocess
import time



path = "/home/hafize/computationalSurgineering/surgical-tracking-last-version/src/"
def run_server():
    subprocess.run(['python', path + 'tcp_server.py'])

def run_main():
    subprocess.run(['python', path + 'main_tcp.py'])
    




if __name__ == "__main__":
    
    server_process = subprocess.Popen(['python', path + 'tcp_server.py'])
    
    main_process = subprocess.Popen(['python', path + 'main_tcp.py'])
    try:
        # Wait for both processes to finish
        server_process.wait()
        main_process.wait()
    except KeyboardInterrupt:
        # If the user interrupts, terminate both processes
        server_process.terminate()
        main_process.terminate()
    