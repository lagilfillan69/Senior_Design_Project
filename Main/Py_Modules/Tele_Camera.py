# Written by Jonah Earl Belback

# Stable container for Telescopic Camera

import cv2,math,platform,subprocess,time

try:
    from helper_functions import *
    from SD_constants import TELECAM_PORT,TELECAM_GND_HEIGHT,TELECAM_FOCAL_LENGTH #needs to be manually set
except Exception as e:
    from Py_Modules.helper_functions import *
    from Py_Modules.SD_constants import TELECAM_PORT,TELECAM_GND_HEIGHT,TELECAM_FOCAL_LENGTH #needs to be manually set
    #raise RuntimeError("Import Error:\n") from e




class TeleCAM():
    def __init__(self, index=TELECAM_PORT,
                 GND_Height=TELECAM_GND_HEIGHT,
                 FocalLength=TELECAM_FOCAL_LENGTH):
        self.GND_Height = GND_Height
        self.H_DegView = math.degrees(2*math.atan(  22.3/(2*FocalLength) ))#prev:FL*16 (realistic? was not)
        self.V_DegView = math.degrees(2*math.atan(  14.9/(2*FocalLength) ))
        
        try:
            if platform.system() == 'Linux': self.SetupCam(index)
            
            self.capture = cv2.VideoCapture(index)
            
            #get shape
            t_frame = self.get_feed()
            self.height,self.width,self.layers = t_frame.shape
            prLightPurple(f'DEPTH CAM:\t<{self.width}> w,  <{self.height}> h,  <{self.layers}> layers')
            print(Back.GREEN+"SUCCESS: TELESCOPIC CAMERA INIT PASS"+Style.RESET_ALL)
        except Exception as e:
            prALERT(f"Error starting 'TeleCAM', switch to Fake?:\ty?")
            if input(">").lower() == 'y': self.fail=True
            else: raise RuntimeError("Error loading Real TeleCAM") from e
    
    #---------------------------------------------------------------------
    
    def SetupCam(self,index,campath="/dev/video"):
        prYellow("Setting up Telescopic Camera w/ gphoto2")
        #-----
        prYellow("--TCAM: create virtual camera device")
        #subprocess.run("bash -c 'sudo modprobe v4l2loopback exclusive_caps=1'", shell=True)
        res = subprocess.run("sudo modprobe v4l2loopback exclusive_caps=1", shell=True, capture_output=True, text=True)
        #if res.returncode != 0: raise RuntimeError(f"TELECAM Setup Fail: create virtual device\n{res.stderr.strip()}")
        if res.returncode != 0: prALERT("!!!!!!! WARNING !!!!!!!\nCouldn't create v4l2loopback DSLR webcam object for Telescopic Camera;\nBe aware of unexpected error before end of this INIT")

        prYellow("--TCAM: kill gphoto (drive connect edgecase)")
        res = subprocess.run("pkill gphoto", shell=True, capture_output=True, text=True)
        #if res.returncode != 0: raise RuntimeError(f"TELECAM Setup Fail: kill gphoto\n{res.stderr.strip()}")

        prYellow("--TCAM: connect to camera")
        self.StreamProc = subprocess.Popen(f"gphoto2 --stdout --capture-movie | ffmpeg -i - -vcodec rawvideo -pix_fmt yuv420p -f v4l2 {campath}{index}",
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                            )
        prYellow("Giving time for Telescopic camera to startup")
        time.sleep(5)

        #if self.StreamProc.poll() is not None: raise RuntimeError(f"Could not establish connection to camera:\n{self.StreamProc.stderr.read().decode()}")
        #if self.StreamProc.poll() is not None: raise RuntimeError(f"Could not establish connection to camera")
        self.fail=False
    	
    	
    	
    
    #---------------------------------------------------------------------
    
    def get_feed(self):
        ret, frame = self.capture.read()
        if not ret: raise RuntimeError("Can't receive frame (stream end?)")
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
