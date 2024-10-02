# Written by Jonah Earl Belback

# Stable container for Telescopic Camera

import cv2,sys,os

dir_path = os.path.abspath("")
print(f"DIRECTORY:\t\t<{dir_path}>")
sys.path.append(dir_path)
from fun_colors import *



class TeleCAM():
    def __init__(self, index):
        self.capture = cv2.VideoCapture(index)
        
        #get shape
        t_frame = self.get_feed()
        self.width,self.height,self.layers = t_frame.shape
        prLightPurple(f'TELE CAM:\t<{self.width}> w,  <{self.height}> h,  <{self.layers}> layers')
        print(Back.GREEN+"SUCCESS: TELESCOPIC CAMERA INIT PASS"+Style.RESET_ALL)
    
    #---------------------------------------------------------------------
        
    def get_feed(self):
        ret, frame = self.capture.read()
        if not ret: raise KeyError("Can't receive frame (stream end?)")
        return frame
    
    def display_feed(self):
        while True:
            cv2.imshow('frame; <q key> to quit', self.get_feed())

            # Press 'q' to exit
            if cv2.waitKey(1) == ord('q'): break
    
    #---------------------------------------------------------------------
    def get_relativeANGLE(self, PIXEL_x,PIXEL_y):
        pass


#==========================================================

#https://stackoverflow.com/questions/57577445/list-available-cameras-opencv-python
def list_ports():
    """
    Test the ports and returns a tuple with the available ports and the ones that are working.
    """
    non_working_ports = []
    dev_port = 0
    working_ports = []
    available_ports = []
    while len(non_working_ports) < 6: # if there are more than 5 non working ports stop the testing. 
        camera = cv2.VideoCapture(dev_port)
        if not camera.isOpened():
            non_working_ports.append(dev_port)
            print("Port %s is not working." %dev_port)
        else:
            is_reading, img = camera.read()
            w = camera.get(3)
            h = camera.get(4)
            if is_reading:
                print("Port %s is working and reads images (%s x %s)" %(dev_port,h,w))
                working_ports.append(dev_port)
            else:
                print("Port %s for camera ( %s x %s) is present but does not reads." %(dev_port,h,w))
                available_ports.append(dev_port)
        dev_port +=1
    return available_ports,working_ports,non_working_ports



#==========================================================
#Test Cases


if __name__ == "__main__":
    available_ports,working_ports,non_working_ports=list_ports()
    print(available_ports,working_ports,non_working_ports)
    
    Tele_camera = TeleCAM(working_ports[0])
    Tele_camera.display_feed()