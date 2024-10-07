# Main on Jettson
# Uses modules avalible to it in Py_Modules directory

# Primary Main: Responsible for decision making process, tells ESP32 what to do through serial
#   - see Serial_Comms

from Py_Modules.YOLOv8.JEB382_YOLOv8_CONTv1 import YOLO_model_v1
from Py_Modules.Stereo_Camera import Stereo_Camera
from Py_Modules.Tele_Camera  import TeleCAM
from Py_Modules.Serial_Comms import Serial_ESP32
from Py_Modules.SD_constants import STEREOCAM_MODELPATH,TELECAM_MODELPATH

import os,sys
dir_path = os.path.abspath("")
print(f"DIRECTORY:\t\t<{dir_path}>")
sys.path.append(dir_path)
from fun_colors import *


class PRIM_Main_Jetson():
    def __init__(self,
                 StereoCamera_ModelPath=STEREOCAM_MODELPATH,
                 TeleCamera_ModelPath=TELECAM_MODELPATH,
                 ):
        
        
        #-----------------------------
        #Telescopic Camera
        print(Back.CYAN+("="*24)+Style.RESET_ALL)
        prCyan("TELESCOPIC Camera initialization")
        self.TeleCam = TeleCAM()
        
        #Telescopic YOLO Model
        prCyan("TELESCOPIC Camera **ML MODEL** initialization")
        self.TeleCam_Model = YOLO_model_v1(model_path=TeleCamera_ModelPath)
        
        
        
        #-----------------------------
        #Stereo Camera
        print(Back.CYAN+("="*24)+Style.RESET_ALL)
        prCyan("STEREO Camera initialization")
        self.SterCam = Stereo_Camera()
        
        #Telescopic YOLO Model
        prCyan("STEREO Camera **ML MODEL** initialization")
        self.TeleCam_Model = YOLO_model_v1(model_path=StereoCamera_ModelPath)
        
        
        
        #-----------------------------        
        #Serial Communication to ESP32
        print(Back.CYAN+("="*24)+Style.RESET_ALL)
        prCyan("Serial Communication initialization")
        self.SerialComms = Serial_ESP32()
        
        
        
        
        #----------------------------- 
        print(Back.GREEN+("="*24)+Style.RESET_ALL)
        print(Back.GREEN+"PYTHON MAIN INIT COMPLETE"+Style.RESET_ALL)
        print(Back.GREEN+("="*24)+Style.RESET_ALL)