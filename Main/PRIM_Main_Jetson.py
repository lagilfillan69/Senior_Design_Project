# Main on Jettson
# Uses modules avalible to it in Py_Modules directory

# Primary Main: Responsible for decision making process, tells ESP32 what to do through serial
#   - see Serial_Comms

import os,sys,platform,time,subprocess
dir_path = os.path.abspath("").replace('\\','/')
if __name__ == "__main__": print(f"DIRECTORY:\t\t<{dir_path}>")
sys.path.append(dir_path)

#------------------------
print(platform.system())
from Py_Modules.helper_functions import *
from Py_Modules.JEB382_YOLOv8 import YOLO_model_v1
from Py_Modules.Stereo_Camera import Stereo_Camera
from Py_Modules.Tele_Camera  import TeleCAM
from Py_Modules.Serial_Comms import Serial_Ard, Serial_Ard_FAKE
from Py_Modules.SD_constants import STEREOCAM_MODELPATH,TELECAM_MODELPATH,CROPCOMPR_FILEPATH
from Py_Modules.Path_Planning import generate_path
prGreen("PRIMARY MAIN Jetson: Import Success")

#------------------------




#===============================================================================


class PRIM_Main_Jetson():
    def __init__(self,
                 StereoCamera_ModelPath=STEREOCAM_MODELPATH,
                 TeleCamera_ModelPath=TELECAM_MODELPATH,
                 Real=True,
                 RealSystem=True
                 ):
        #cover cases for when parts of system aren't real
        self.TeleCam=None;self.TeleCam_Model=None;self.SterCam=None;self.SterCam_Model=None
        
        self.Real=Real
        if platform.system() != 'Linux': self.RealSystem=False
        else: self.RealSystem=RealSystem
        
        prYellow(f"Real??\t{self.Real}")
        prYellow(f"Real System??\t{self.RealSystem}")
        
        #-----------------------------
        #Telescopic Camera
        print(Back.CYAN+("="*24)+Style.RESET_ALL)
        prCyan("TELESCOPIC Camera initialization")
        
        #NOTE: !!!!!!!!!!!!!!!   commenting out for current objectives
        
        #if self.RealSystem: self.TeleCam = TeleCAM()
        
        #Telescopic YOLO Model
        prCyan("TELESCOPIC Camera **ML MODEL** initialization")
        if self.Real: self.TeleCam_Model = YOLO_model_v1(model_path=TeleCamera_ModelPath)
        
        
        
        #-----------------------------
        #Stereo Camera
        print(Back.CYAN+("="*24)+Style.RESET_ALL)
        prCyan("STEREO Camera initialization")
        if self.RealSystem: self.SterCam = Stereo_Camera(Real=self.Real)
        
        #Telescopic YOLO Model
        prCyan("STEREO Camera **ML MODEL** initialization")
        if self.Real: self.SterCam_Model = YOLO_model_v1(model_path=StereoCamera_ModelPath)
        
        
        
        #-----------------------------        
        #Serial Communication to ESP32
        print(Back.CYAN+("="*24)+Style.RESET_ALL)
        prCyan("Serial Communication initialization")
        if self.RealSystem: self.SerialComms = Serial_Ard()
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
        self.Tele_angles = None #Relative Angles - 1xN, 1D
        self.Stereo_Items = None #Relative [Angle, Depth] - 2xN, 2D

        #-----
        Previous_State = 0
        Curr_State = 0
        Current_Cordinate = []  #use??????, is this a duplicate of Current_Location??
        Path=[]
        Path_Index = -2
        Current_Location = [0,0]
        Runway_Boundaries=None
        Trash_Collected_Locations = []  #use?????? set but not used, send to UI?
        Trash_Index = -1
        
        #====================================================================
        while True:            
            if cv2.waitKey(1) == ord('q'):
                prALERT("STOPPING PRIMARY JETSON MAIN: 'Q' key QUIT")
                return
            
            #get message if there is
            message = self.SerialComms.read_message()
            # if not self.Real: prGreen(f'<{message}>')
            if message is None: continue
            
            
            #printing
            if not self.Real:
                print(message,end="\t")
                prCyan(f"Curr,Prev,  DetBound,  PathIdx,PathLen,PathTarg,  currTrashTarg\t\t[{Curr_State}, {Previous_State},   {Runway_Boundaries},   {Path_Index}, {len(Path)}, { f'[{Path[Path_Index][0]}, {Path[Path_Index][1]}]' if (Path is not None and Path_Index>=0) else None },   {self.Stereo_Items[Trash_Index] if self.Stereo_Items is not None else None}]")
                #print(message.split('\t'))
            
            
            #STOP STATE 
            if message == "STOP":
                #raise RuntimeError("STOPPING PRIMARY JETSON MAIN: STOP MESSAGE")
                #-----
                #Resetting
                self.Tele_angles = None #Relative Angles - 1xN, 1D
                self.Stereo_Items = None #Relative [Angle, Depth] - 2xN, 2D
                Previous_State = 0
                Curr_State = 0
                Current_Cordinate = []  #use??????, is this a duplicate of Current_Location??
                Path=[]
                Path_Index = -2
                Current_Location = [0,0]
                Runway_Boundaries=None
                Trash_Collected_Locations = []  #use?????? set but not used, send to UI?
                Trash_Index = -1
                #-----
                
                while True:
                    if cv2.waitKey(1) == ord('q'):
                        prALERT("STOPPING PRIMARY JETSON MAIN: 'Q' key QUIT; in pause loop")
                        return
                    
                    message = self.SerialComms.read_message()
                    if message is None: continue
                    
                    if message.split('\t')[0] == "STAR":
                        for ele in message.split('\t')[1][1:-1].split(':') :
                            Runway_Boundaries.push(float(ele.split(':')[0]), float(ele.split(':')[1]))
                        Previous_State = Curr_State
                        Curr_State = 1
                        prALERT("RESUME PRIMARY JETSON MAIN")
                        break
                    elif not message is None: prRed(f"Incoming Message but not 'STAR' to restart:\t{message}")
            
            #PAUSE STATE (2) 
            elif message == "PAUS":
                Previous_State = Curr_State
                Curr_State = 2 #not necessairy but for redundancy
                prALERT("PAUSING PRIMARY JETSON MAIN: PAUSE MESSAGE")
                while True:
                    if cv2.waitKey(1) == ord('q'):
                        prALERT("STOPPING PRIMARY JETSON MAIN: 'Q' key QUIT; in pause loop")
                        return
                    
                    message = self.SerialComms.read_message()
                    if message == "PAUS":
                        prALERT("RESUME PRIMARY JETSON MAIN")
                        Curr_State = Previous_State
                        Previous_State = 2
                        break
                    elif not message is None: prRed(f"Incoming Message but not 'PAUS' to unpause:\t{message}")
            
            #### Update location -- not a state
            #structure: 'CPOS\t[  4 floating point values  ]
            #   ex (do own tab):   CPOS\t[3, 12]
            elif message.split('\t')[0] == "CPOS":
                Current_Location = [ float(ele) for ele in message.split('\t')[1][1:-1].split(',') ]

            ### START STATE ###
            #structure: 'STAR\t[  4 floating point values  ]
            #   ex (do own tab):   STAR\t[(p1,p2,p3)
            elif message.split('\t')[0] == "STAR" and (Curr_State == 0 or Curr_State == 2) :
                #NOTE: !!!!!!! Lauren FIX
                #for ele in message.split('\t')[1][1:-1].split(':') :
                #    Runway_Boundaries.push(float(ele.split(':')[0]), float(ele.split(':')[1]))

                Previous_State = Curr_State
                Curr_State = 1
            
            ### WAITING FOR APPROVAL STATE
            elif message == "OKAY" and Curr_State == 5 :
                Previous_State = Curr_State
                Curr_State = 6
    
            elif message == "NKAY" and Curr_State == 5 : #Object Located (waiting)
                #original point state, goes to next point in path
                # Previous_State = Curr_State
                # Curr_State = 6
                Path_Index+=1

            ### Waiting to arrive at precise location state (STATE 7)
            elif message.split('\t')[0] == "ARSR" and Curr_State == 7:
                Current_Location = [ float(ele) for ele in message.split('\t')[1][1:-1].split(',') ]
                self.SerialComms.Bluetooth("To bluetooth : Trash Picked Up")
                # self.SerialComms.Search_GoTo("Return to this cord") #NOTE Is this not handled by other comms from other states???? Is this Search??
                Previous_State = Curr_State
                Curr_State = 8
            
            #TAKE PICTURE AND SAVE to folder
            elif message == "CAMR" and self.RealSystem:
                dstr=datestr()
                if not self.SterCam is None: cv2.imwrite("/DataCollect/Stereo/{dstr}.jpg",     self.SterCam.get_feed())
                if not self.TeleCam is None: cv2.imwrite("/DataCollect/Telescopic/{dstr}.jpg", self.TeleCam.get_feed())
            

                
            
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
                #NOTE: !!!!!!! Lauren FIX
                #Path = generate_path(Runway_Boundaries1[0],Runway_Boundaries1[1],Runway_Boundaries1[2])
                
                #NOTE: !!!!!!! 
                #TEST
                self.SerialComms.Collect_GoTo([10,1])
                '''
                while True:
                    print('.',end='')
                    self.SerialComms.Collect_GoTo([10,1])
                    time.sleep(1)
                '''
                
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
                    # self.SerialComms.send_message("OBJ FOUND") #NOTE: Is this right? Are we sending a message like this to the Arduino???????
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
                    # self.SerialComms.send_message("OBJ FOUND @ RELATIVE LOCATION") #NOTE: Is this right? Are we sending a message like this to the Arduino???????
                else:
                    #object is lost, what do we do?
                    Curr_State = 6
                    Previous_State = 6
                    # self.SerialComms.send_message("RELATIVE OBJ LOSS") #NOTE: Is this right? Are we sending a message like this to the Arduino???????
                    
            #===========================================================
            #Drive to Object (precise)
            elif(Curr_State == 7):
                if not self.Real: prLightPurple(f"EXEC State {Curr_State}")
                # self.SerialComms.send_message("To Motor Driver : Drive to [X,Y] location")
                self.SerialComms.Search_GoTo(self.Stereo_Items[Trash_Index])

                # will stay in this state until we are at set locations
                if(Current_Location == self.Stereo_Items[Trash_Index]):
                    Curr_State = 8
                else : 
                    Curr_State = 7
                Previous_State = Curr_State

            #Vaccum Object
            elif(Curr_State == 8):
                if not self.Real: prLightPurple(f"EXEC State {Curr_State}")
                print("Turn on Vaccum, wait 30 seconds, turn off vaccum")
                self.SerialComms.Vaccum()
                time.sleep(30)
                self.SerialComms.Vaccum()                
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
            
            
            #-------------------
            #printing
            if not self.Real:
                prYellow(f"{message}\tCurr,Prev,  DetBound,  PathIdx,PathLen,PathTarg,  currTrashTarg\t\t[{Curr_State}, {Previous_State},   {Runway_Boundaries},   {Path_Index}, {len(Path)}, { f'[{Path[Path_Index][0]}, {Path[Path_Index][1]}]' if (Path is not None and Path_Index>=0) else None },   {self.Stereo_Items[Trash_Index] if self.Stereo_Items is not None else None}]")
                
               
        
    def detect_Tele(self):
        #check telescopic camera for objects and their relative Angle
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
        #check Stereo Camera for objects and their relative [ Angle, Depth ]
        if self.Real:
            Stereo_photo = self.SterCam.get_feed()
            Stereo_results = self.SterCam_Model.run_model( Stereo_photo  )
            if Stereo_results is not None:
                self.Stereo_Items = [ self.SterCam.get_relativeAngDep( find_center(res[1]) ) for res in Stereo_results ] #list of relative positions of trash
                #outputs cropped & compressed pictures of trash
                if save_image:
                    for index,res in enumerate(Stereo_results):
                        reduce_ImgObj( img= Stereo_photo,
                                       coords=find_center(res[1]),
                                       output_path=f"{CROPCOMPR_FILEPATH}{res[0]}_{index}___{goodtime()}" )
                return True
            else:
                self.Stereo_Items = None
                return False
        else:
            if input('>S>>')=='y':
                self.Stereo_Items = [   [6,12], [3,12]   ]
                return True
            else:
                self.Stereo_Items = None
                return False



prGreen("PRIMARY MAIN Jetson: Class Definition Success")
#===============================================================================



if __name__ == "__main__":
    eevee = PRIM_Main_Jetson(Real=False)#,RealSystem=False)
    eevee.MainProject_Loop()
