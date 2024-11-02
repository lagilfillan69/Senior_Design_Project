# Written by Jonah Earl Belback

# Stable container for Telescopic Camera

import cv2,math,platform

try:
    from helper_functions import *
    from SD_constants import TELECAM_PORT,TELECAM_GND_HEIGHT,TELECAM_FOCAL_LENGTH #needs to be manually set
except:
    if platform.system() != 'Linux':
        from Py_Modules.helper_functions import *
        from Py_Modules.SD_constants import TELECAM_PORT,TELECAM_GND_HEIGHT,TELECAM_FOCAL_LENGTH #needs to be manually set
    else:
        from snr_proj.helper_functions import *
        from snr_proj.SD_constants import TELECAM_PORT,TELECAM_GND_HEIGHT,TELECAM_FOCAL_LENGTH #needs to be manually set




class TeleCAM():
    def __init__(self, index=TELECAM_PORT,
                 GND_Height=TELECAM_GND_HEIGHT,
                 FocalLength=TELECAM_FOCAL_LENGTH):
        self.GND_Height = GND_Height
        self.H_DegView = math.degrees(2*math.atan(  22.3/(2*FocalLength) ))#prev:FL*16 (realistic? was not)
        self.V_DegView = math.degrees(2*math.atan(  14.9/(2*FocalLength) ))
        
        self.capture = cv2.VideoCapture(index)
        
        #get shape
        t_frame = self.get_feed()
        self.height,self.width,self.layers = t_frame.shape
        prLightPurple(f'DEPTH CAM:\t<{self.width}> w,  <{self.height}> h,  <{self.layers}> layers')
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
    
    #helper func for get_relativePOSITION and get_size
    #pos: angle to the right
    #neg: angle to the left
    def get_relativeANGLEX(self, coord):
        mid = self.width/2
        diff = mid - coord[0]
        
        #left
        if diff>0: return -abs(diff) * self.H_DegView/self.width
        #right
        elif diff<0: return abs(diff) * self.H_DegView/self.width
        #middle
        else: return 0
    
    #Not sure if we'll use
    def get_relativeANGLEY(self, coord):
        mid = self.height/2
        diff = mid - coord[1]
        
        #left
        if diff>0: return -abs(diff) * self.V_DegView/self.height
        #right
        elif diff<0: return abs(diff) * self.V_DegView/self.height
        #middle
        else: return 0



prGreen("TeleCAM: Class Definition Success")
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
    # available_ports,working_ports,non_working_ports=list_ports()
    # print(available_ports,working_ports,non_working_ports)
    
    # Tele_camera = TeleCAM(working_ports[0])
    Tele_camera = TeleCAM(0)
    Tele_camera.display_feed()
