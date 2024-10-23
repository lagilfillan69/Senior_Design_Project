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
from Py_Modules.Serial_Comms import Serial_Ard, Serial_Ard_FAKE
from Py_Modules.SD_constants import STEREOCAM_MODELPATH,TELECAM_MODELPATH,CROPCOMPR_FILEPATH
from Py_Modules.Path_Planning import PathPlan
prGreen("PRIMARY MAIN Jetson: Import Success")

#------------------------




#===============================================================================


class PRIM_Main_Jetson():
    def __init__(self,
                 StereoCamera_ModelPath=STEREOCAM_MODELPATH,
                 TeleCamera_ModelPath=TELECAM_MODELPATH,
                 Real=True
                 ):
        self.Real = Real
        
        #-----------------------------
        #Telescopic Camera
        print(Back.CYAN+("="*24)+Style.RESET_ALL)
        prCyan("TELESCOPIC Camera initialization")
        self.TeleCam = TeleCAM()
        
        #Telescopic YOLO Model
        prCyan("TELESCOPIC Camera **ML MODEL** initialization")
        if self.Real: self.TeleCam_Model = YOLO_model_v1(model_path=TeleCamera_ModelPath)
        
        
        
        #-----------------------------
        #Stereo Camera
        print(Back.CYAN+("="*24)+Style.RESET_ALL)
        prCyan("STEREO Camera initialization")
        self.SterCam = Stereo_Camera(Real=self.Real)
        
        #Telescopic YOLO Model
        prCyan("STEREO Camera **ML MODEL** initialization")
        if self.Real: self.SterCam_Model = YOLO_model_v1(model_path=StereoCamera_ModelPath)
        
        
        
        #-----------------------------        
        #Serial Communication to ESP32
        print(Back.CYAN+("="*24)+Style.RESET_ALL)
        prCyan("Serial Communication initialization")
        if self.Real: self.SerialComms = Serial_Ard()
        else: self.SerialComms = Serial_Ard_FAKE()
        
        
        
        
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
        
        #-----
        self.Tele_angles = None
        self.Stereo_Pos = None

        #-----
        Previous_State = 0
        Curr_State = 0
        Current_Cordinate = []  #use??????
        Path=[]
        Path_Index = -2
        Current_Location = [0,0]
        Runway_Boundaries=None
        Trash_Collected_Locations = []  #use??????
        Trash_Index = -1
        
        #====================================================================
        while True:
            if not self.Real:
                prCyan(f"Curr,Prev,  DetBound,  PathIdx,PathLen,PathTarg,  currTrashTarg\t\t[{Curr_State}, {Previous_State},   {Runway_Boundaries},   {Path_Index}, {len(Path)}, { f'[{Path[Path_Index][0]}, {Path[Path_Index][1]}]' if (Path is not None and Path_Index>=0) else None },   {self.Stereo_Pos[Trash_Index] if self.Stereo_Pos is not None else None}]")

            
            if cv2.waitKey(1) == ord('q'):
                prALERT("STOPPING PRIMARY JETSON MAIN: 'Q' key QUIT")
                return
            
            #get message if there is
            message = self.SerialComms.read_message()
            # if not self.Real: prGreen(f'<{message}>')
            
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
                    if message == "RESUME_MESSAGE":
                        prALERT("RESUME PRIMARY JETSON MAIN")
                        Curr_State = Previous_State
                        Previous_State = 2
                        break
            
            #### Update location -- not a state
            #structure: 'LOC_MESSAGE\t[  4 floating point values  ]
            #   ex (do own tab):   LOC_MESSAGE\t[3, 12]
            elif message.split('\t')[0] == "LOC_MESSAGE":
                Current_Location = [ float(ele) for ele in message.split('\t')[1][1:-1].split(',') ]#message  #TODO: Decode

            ### START STATE ###
            #structure: 'START_MSG\t[  4 floating point values  ]
            #   ex (do own tab):   START_MSG\t[40.35729, -79.93397, 40.35604, -79.93218]
            elif message.split('\t')[0] == "START_MSG" and (Curr_State == 0 or Curr_State == 2) :
                Runway_Boundaries = [ float(ele) for ele in message.split('\t')[1][1:-1].split(',') ]
                Previous_State = Curr_State
                Curr_State = 1
            
            ### WAITING FOR APPROVAL STATE
            elif message == "APPROVAL_MESSAGE" and Curr_State == 5 :
                Previous_State = Curr_State
                Curr_State = 6
    
            elif message == "DISAPPROVAL_MESSAGE" and Curr_State == 5 : #Object Located (waiting)
                #original point state, goes to next point in path
                # Previous_State = Curr_State
                # Curr_State = 6
                Path_Index+=1

            ### Waiting to arrive at precise location state (STATE 7)
            elif message == "ARRIVED_AT_TRASH_MESSAGE" and Curr_State == 7:
                self.SerialComms.send_message("To bluetooth : Trash Picked Up")
                self.SerialComms.send_message("Return to this cord")
                Previous_State = Curr_State
                Curr_State = 8
            

                
            
            #regular run
            # else:
            #READY TO START
            if Curr_State == 0:
                if not self.Real: prLightPurple(f"EXEC State {Curr_State}")
                #------
                continue
            
            #START 
            elif(Curr_State == 1):
                if not self.Real: prLightPurple(f"EXEC State {Curr_State}")
                #------
                Path = PathPlan(Runway_Boundaries)
                Path_Index = -1 
                Previous_State = Curr_State
                Curr_State = 3


            #Go to Next Path Index
            elif(Curr_State == 3):
                if not self.Real: prLightPurple(f"EXEC State {Curr_State}")
                #------
                #edge case, try to travel with no path
                if(Path_Index == -2):
                    Curr_State = 0
                else :
                    Path_Index += 1
                    # prRed(f'{Current_Location}, {Path[Path_Index]}')
                    # prRed(f'{Current_Location[0]}, {Path[Path_Index][0]}')
                    # prRed(f'{Current_Location[1]}, {Path[Path_Index][1]}')
                    if(Path_Index > len(Path)-1):
                        Path_Index = -2
                        Curr_State = 0
                    elif (Current_Location[0] == Path[Path_Index][0]) or (Current_Location[1] == Path[Path_Index][1]):
                        Curr_State = 4
                    else:
                        Curr_State = 3
                Previous_State = 3

            #Detect Objects
            elif(Curr_State == 4):
                if not self.Real: prLightPurple(f"EXEC State {Curr_State}")
                #------
                #TODO: SOMEWHERE HERE go to self.Tele_angles[ang_ind]
                    
                if Previous_State != 4:
                    start_time = time.time()
                if self.detect_Tele(): 
                    Curr_State = 5 
                    self.SerialComms.send_message("OBJ FOUND")
                elif (time.time() - start_time > 60):
                    Curr_State = 3 # go to next point, nothing is detected here
                else :
                    Curr_State = 4
                Previous_State = 4

            #Object Located (Notify Officals)
            elif(Curr_State == 5):
                if not self.Real: prLightPurple(f"EXEC State {Curr_State}:  <waiting for approval>")
                #------
                #Dead state while waiting for officals
                Previous_State = Curr_State

            #Drive to Object (relative)
            elif(Curr_State == 6):
                if not self.Real: prLightPurple(f"EXEC State {Curr_State}")
                #------
                ### TODO @Jonah add in ur piece to this
                #Will stay in this state until there is a precise location found or object is lost
                #precise location: Stereo Camera
                if self.detect_Stereo(): 
                    Curr_State = 7 
                    self.SerialComms.send_message("OBJ FOUND @ RELATIVE LOCATION")
                else:
                    #object is lost, what do we do?
                    Curr_State = 6
                    Previous_State = 6
                    self.SerialComms.send_message("RELATIVE OBJ LOSS")
                    
            #===========================================================
            #Drive to Object (precise)
            elif(Curr_State == 7):
                if not self.Real: prLightPurple(f"EXEC State {Curr_State}")
                self.SerialComms.send_message("To Motor Driver : Drive to [X,Y] location")

                # will stay in this state until we are at set locations
                if(Current_Location == self.Stereo_Pos[Trash_Index]):
                    Curr_State = 8
                else : 
                    Curr_State = 7
                Previous_State = Curr_State

            #Vaccum Object
            elif(Curr_State == 8):
                if not self.Real: prLightPurple(f"EXEC State {Curr_State}")
                print("Turn on Vaccum, wait 30 seconds, turn off vaccum")
                Trash_Collected_Locations.append(Current_Location)
                Curr_State = 9
                Previous_State = Curr_State
            
            # 9 - Return to Path Cord
            elif(Curr_State == 9):
                if not self.Real: prLightPurple(f"EXEC State {Curr_State}")
                #will stay in this stay in this state until cordinates are reached
                if (Current_Location[0] == Path[Path_Index][0]) or (Current_Location[1] == Path[Path_Index][1]):
                    Curr_State = 4
                else :
                    Curr_State = 9
                Previous_State = Curr_State
                
               
        
    def detect_Tele(self):
        #check telescopic camera for objects
        if self.Real:
            Tele_results = self.TeleCam_Model.run_model(  self.TeleCam.get_feed()  )
            if Tele_results is not None:
                self.Tele_angles = [self.TeleCam.get_relativeANGLEX(res) for res in Tele_results]
                return True
            else:
                self.Tele_angles = None
                return False
        else:
            if input('>T>>')=='y':
                self.Tele_angles = [26.565, 14.036]
                return True
            else:
                self.Tele_angles = None
                return False

    def detect_Stereo(self,save_image=False):
        #check Stereo Camera for objects and their relative positions
        if self.Real:
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
        else:
            if input('>S>>')=='y':
                self.Stereo_Pos = [   [6,12], [3,12]   ]
                return True
            else:
                self.Stereo_Pos = None
                return False



prGreen("PRIMARY MAIN Jetson: Class Definition Success")
#===============================================================================



if __name__ == "__main__":
    eevee = PRIM_Main_Jetson(Real=False)
    eevee.MainProject_Loop()
