import time
import cv2 #sudo apt-get install python-opencv
import json
import os
from datetime import datetime
import argparse
from arducam_camera import MyCamera
from utils import ArducamUtils

def write_camera_params(fmt):
    result = json.dumps(fmt, sort_keys=True, indent=4, separators=(',',':'))
    fName = 'camera_params.txt'
    f = open(str(fName), 'w') 
    f.write(result)
    f.close()

def parse_cmdline():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--device', default=0, type=int, nargs='?',
                        help='/dev/videoX default is 0')
    parser.add_argument('--width', type=lambda x: int(x,0), default=-1,
                        help="set width of image")
    parser.add_argument('--height', type=lambda x: int(x,0),default=-1,
                        help="set height of image")

    args = parser.parse_args()
    return args

# File for captured image
filename = './scenes/photo-2.png'
WIDTH = 1920
HEIGHT = 1080
if __name__ == "__main__":
    args = parse_cmdline()
    try:
        camera = MyCamera()
        print("Open camera...")
        camera.open_camera(args.device, WIDTH, HEIGHT)
        # (width, height) = camera.get_framesize()
        (width, height) = (1000, 200)
        print("Current resolution: {}x{}".format(width, height))
        fmt = {
            'device': args.device,
            'width': width,
            'height': height,
        }
        
        frame = None
        t2 = datetime.now()
        counter = 0
        avgtime = 0
        
        scale = 1280.0 / fmt['width']
        fmt['scale'] = scale
        image_width = int(fmt['width'] * scale)
        image_height = int(fmt['height'] * scale)

        frame = camera.get_frame()
        frame = cv2.resize(frame, (image_width, image_height))
        cv2.imshow("Arducam", frame)

        while cv2.waitKey(10) != ord('q'):
            counter+=1
            frame = camera.get_frame()
            frame = cv2.resize(frame, (image_width, image_height))
            cv2.imshow("Arducam", frame)
            if counter == 10 :
                write_camera_params(fmt)
                cv2.imwrite(filename, frame)

            
        t1 = datetime.now()
        timediff = t1-t2
        avgtime = avgtime + (timediff.total_seconds())
        avgtime = avgtime/counter
        print ("Average time between frames: " + str(avgtime))
        print ("Average FPS: " + str(1/avgtime))
        if (os.path.isdir("./scenes")==False):
            os.makedirs("./scenes")
        
        write_camera_params(fmt)
        cv2.imwrite(filename, frame)
        print("Close camera...")
        camera.close_camera()
    except Exception as e:
        print(e)

        
