# Main on Jettson
# Uses modules avalible to it in Py_Modules directory

# Primary Main: Responsible for decision making process, tells ESP32 what to do through serial
#   - see Serial_Comms

from Py_Modules.YOLOv8.JEB382_YOLOv8_CONTv1 import YOLO_model_v1
from Py_Modules.Stereo_Camera import Stereo_Camera
from Py_Modules.Tele_Camera  import TeleCAM
from Py_Modules.Serial_Comms import Serial_ESP32
from Py_Modules.SD_constants import STEREOCAM_MODELPATH,TELECAM_MODELPATH,CROPCOMPR_FILEPATH

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
        self.SterCam_Model = YOLO_model_v1(model_path=StereoCamera_ModelPath)
        
        
        
        #-----------------------------        
        #Serial Communication to ESP32
        print(Back.CYAN+("="*24)+Style.RESET_ALL)
        prCyan("Serial Communication initialization")
        self.SerialComms = Serial_ESP32()
        
        
        
        
        #----------------------------- 
        print(Back.GREEN+("="*24)+Style.RESET_ALL)
        print(Back.GREEN+"PYTHON MAIN INIT COMPLETE"+Style.RESET_ALL)
        print(Back.GREEN+("="*24)+Style.RESET_ALL)
        
        
        
        
    def MainProject_Loop(self):
        while True:
            if cv2.waitKey(1) == ord('q'):
                prALERT("STOPPING PRIMARY JETSON MAIN: 'Q' key QUIT")
                return
            
            #get message if there is
            message = self.SerialComms.read_message()            
            
            #stoppage
            if message == "STOP_MESSAGE":   #NOTE: This is temp code, the actual message for Stopping would be different
                raise KeyError("STOPPING PRIMARY JETSON MAIN: STOP MESSAGE")
            
            #pausing
            elif message == "PAUSE_MESSAGE":   #NOTE: This is temp code, the actual message for Pausing would be different
                prALERT("PAUSING PRIMARY JETSON MAIN: PAUSE MESSAGE")
                while True:
                    if cv2.waitKey(1) == ord('q'):
                        prALERT("STOPPING PRIMARY JETSON MAIN: 'Q' key QUIT; in pause loop")
                        return
                    
                    message = self.SerialComms.read_message()
                    if message == "RESUME MESSAGE":
                        prALERT("RESUME PRIMARY JETSON MAIN")
                        break
            
            #regular run
            else:
                #NOTE: FSM WORK HERE !!!!!!!!!!!!!!!!!!!!!!
                #NOTE: need actual functionality to figure out; current work showed is an example of some nessecary code that'd be in the FSM, not any complete functionality
                
                
                #----------------------------- 
                #NOTE: !!! There'd be some loop (#1) here of scanning area with search pattern
                
                
                #----------------------------- 
                #NOTE: this would be in previous mentioned loop (#1)
                #check telescopic camera for objects
                #   sets self.Tele_angles: list of relative angles
                #   returns if theres any detections
                if not self.detect_Tele(): continue   #if theres no trash, go to begining on While Loop
               
                
                #----------------------------- 
                #NOTE: !!! There'd be some loop (#2) and logic here about following angles of objects from self.Tele_angles
                #   then finer searching with Stereo camera
                
                
                #-----------------------------
                #NOTE: this would be in previous mentioned loop (#2)
                #check Stereo Camera for objects and their relative positions
                #   sets self.Stereo_Pos: list of relative posititions
                #   returns if theres any detections
                if not self.detect_Stereo(): continue   #if theres no trash, go to begining on While Loop
                
                
                #----------------------------- 
                #NOTE: this would be in previous mentioned loop (#2)
                #NOTE: !!! There'd be some loop and logic here about following to detected trash from self.Stereo_Pos, then picking it up
                
            pass
        
    def detect_Tele(self):
        #check telescopic camera for objects
        Tele_results = self.TeleCam_Model.run_model(  self.TeleCam.get_feed()  )
        if Tele_results is not None:
            self.Tele_angles = [self.TeleCam.get_relativeANGLEX(res) for res in Tele_results]
            return True
        else:
            self.Tele_angles = None
            return False

    def detect_Stereo(self,save_image=False):
        #check Stereo Camera for objects and their relative positions
        Stereo_photo = self.SterCam.get_feed()
        Stereo_results = self.SterCam_Model.run_model( Stereo_photo  )
        if Stereo_results is not None:
            self.Stereo_Pos = [ self.SterCam.get_relativePOSITION( find_center(res[1]) ) for res in Stereo_results ] #list of relative positions of trash
            #outputs cropped & compressed pictures of trash
            if save_image:
                for index,res in enumerate(Stereo_results):
                    reduce_found_obj( Stereo_photo,res[1],f"{CROPCOMPR_FILEPATH}{res[0]}_{index}___{goodtime()}" )
            return True
        else:
            self.Stereo_Pos = None
            return False