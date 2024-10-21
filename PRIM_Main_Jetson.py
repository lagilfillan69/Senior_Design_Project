# Main on Jettson
# Uses modules avalible to it in Py_Modules directory

# Primary Main: Responsible for decision making process, tells ESP32 what to do through serial
#   - see Serial_Comms

import os,sys
import time
dir_path = os.path.abspath("").replace('\\','/')
if __name__ == "__main__": print(f"DIRECTORY:\t\t<{dir_path}>")
sys.path.append(dir_path)

#------------------------
from Py_Modules.helper_functions import *
from Py_Modules.JEB382_YOLOv8 import YOLO_model_v1
from Py_Modules.Stereo_Camera import Stereo_Camera
from Py_Modules.Tele_Camera  import TeleCAM
from Py_Modules.Serial_Comms import Serial_Ard
from Py_Modules.SD_constants import STEREOCAM_MODELPATH,TELECAM_MODELPATH,CROPCOMPR_FILEPATH
prGreen("PRIMARY MAIN Jetson: Import Success")

#------------------------




#===============================================================================


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
        self.SerialComms = Serial_Ard()
        
        
        
        
        #----------------------------- 
        print(Back.GREEN+("="*24)+Style.RESET_ALL)
        print(Back.GREEN+"PYTHON MAIN INIT COMPLETE"+Style.RESET_ALL)
        print(Back.GREEN+("="*24)+Style.RESET_ALL)
        
        
        
        
    def MainProject_Loop(self):
        # State Legend
        # 0 - Stop
        # 1 - Start
        # 2 - Pause
        # 3 - Drive to next path coorindates
        # 4 - Detect Objects
        # 5 - Object Located (waiting)
        # 6 - Drive to Object (relative)
        # 7 - Drive to Object (precise)
        # 8 - Vaccum Object
        # 9 - Return to Path Cord


        Previous_State = 0
        Curr_State = 0
        Current_Cordinate = []
        Path_Index = -2
        Current_Location = [0,0]
        Trash_Detected_Locations = []
        Trash_Collected_Locations = []
        Trash_Index = -1
       
        while True:
            if cv2.waitKey(1) == ord('q'):
                prALERT("STOPPING PRIMARY JETSON MAIN: 'Q' key QUIT")
                return
            
            #get message if there is
            # message = self.SerialComms.read_message()
            message = input(">")      
            
            #STOP STATE 
            if message == "STOP_MESSAGE":   #NOTE: This is temp code, the actual message for Stopping would be different
                Curr_State = 0
                Path_Index = -2
                raise KeyError("STOPPING PRIMARY JETSON MAIN: STOP MESSAGE")
            
            #PAUSE STATE (2) 
            elif message == "PAUSE_MESSAGE":   #NOTE: This is temp code, the actual message for Pausing would be different
                Curr_State = 2 #not necessairy but for redundancy
                prALERT("PAUSING PRIMARY JETSON MAIN: PAUSE MESSAGE")
                while True:
                    if cv2.waitKey(1) == ord('q'):
                        prALERT("STOPPING PRIMARY JETSON MAIN: 'Q' key QUIT; in pause loop")
                        return
                    
                    message = self.SerialComms.read_message()
                    if message == "RESUME MESSAGE":
                        prALERT("RESUME PRIMARY JETSON MAIN")
                        Previous_State = 2
                        break
            
            #### Update location -- not a state
            elif message == "LOC MESSAGE":
                Current_Location = message

            ### START STATE ###
            elif message == "START_MSG" and (Curr_State == 0 or Curr_State == 2) :
                Detect_Boundaries = message
                Previous_State = Curr_State
                Curr_State = 1
            
            ### WAITING FOR APPROVAL STATE
            elif message == "APPROVAL MESSAGE " and Curr_State == 5 :
                Previous_State = Curr_State
                Curr_State = 6
    
            elif message == "DISAPPROVAL MESSAGE " and Curr_State == 5 : #Object Located (waiting)
                #original point state, goes to next point in path
                # Previous_State = Curr_State
                # Curr_State = 6
                Path_Index+=1

            ### Waiting to arrive at precise location state (STATE 7)
            elif message == "ARRIVED AT TRASH MESSAGE" and Curr_State == 7:
                Serial_Ard.send_message("To bluetooth : Trash Picked Up")
                Serial_Ard.send_message("Return to this cord")
                Previous_State = Curr_State
                Curr_State = 8
            

                
            
            #regular run
            else:
                
                #READY TO START
                if Curr_State == 0: 
                    continue
                
                #START 
                elif(Curr_State == 1):
                    Path = PathPlan(Detect_Boundaries)
                    Path_Index = -1 
                    Previous_State = Curr_State
                    Curr_State = 3
    

                #Go to Next Path Index
                elif(Curr_State == 3):    
                    #edge case, try to travel with no path
                    if(Path_Index == -2):
                        Curr_State = 0
                    else :
                        Path_Index += 1
                        if(Path_Index > Path.size()-1):
                            Path_Index = -2 
                            Curr_State = 0
                        elif (Current_Location == Path[Path_Index]):
                            Curr_State = 4
                        else : 
                            Curr_State = 3
                    Previous_State = 3

                #Detect Objects
                elif(Curr_State == 4):
                    if Previous_State != 4:
                        start_time = time.time()
                    if self.detect_Tele(): 
                        Curr_State = 5 
                        Serial_Ard.send_message("OBJ FOUND")
                    elif (time.time() - start_time > 60):
                        Curr_State = 3 # go to next point, nothing is detected here
                    else :
                        Curr_State = 4
                    Previous_State = 4

                #Object Located (Notify Officals)
                elif(Curr_State == 5):
                    #Dead state while waiting for officals
                    Previous_State = Curr_State

                #Drive to Object (relative)
                elif(Curr_State == 6):
                    ### TODO @Jonah add in ur piece to this 
                    #Will stay in this state until there is a precise location found or object is lost
                     #what will we deam a lost object? 
                    if self.detect_Stereo() : 
                        Curr_State = 7 
                        Serial_Ard.send_message("OBJ FOUND @ PRECISE LOCATION")
                    else :
                        Serial_Ard.send_message("OBJ FOUND @ RELATIVE LOCATION")
                        Curr_State = 6
                        Previous_State = 6           
                
               
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



prGreen("PRIMARY MAIN Jetson: Class Definition Success")
#===============================================================================



if __name__ == "__main__":
    pass