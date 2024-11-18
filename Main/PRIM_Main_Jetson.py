# Written by Jonah Earl Belback

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
                 Real=[True,True,True], #individual status of modules;   [ Tele, Stereo, Ard ]
                 RealSystem=True,	#if on laptop or on Jetson
                 Forced=False
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
        if self.RealSystem and self.Real[0]:
            self.TeleCam = TeleCAM()
            if self.TeleCam.fail:
                prYellow("Switching to Fake TeleCam")
                self.TeleCam=None
                self.Real[0]=False
            else:
                #Telescopic YOLO Model
                prCyan("TELESCOPIC Camera **ML MODEL** initialization")
                self.TeleCam_Model = YOLO_model_v1(model_path=TeleCamera_ModelPath)
        
        
        
        #-----------------------------
        #Stereo Camera
        print(Back.CYAN+("="*24)+Style.RESET_ALL)
        prCyan("STEREO Camera initialization")
        if self.RealSystem and self.Real[1]:
            self.SterCam = Stereo_Camera()
            if self.SterCam.fail:
                prYellow("Switching to Fake TeleCam")
                self.SterCam=None
                self.Real[1]=False
            else:
                #Stereo YOLO Model
                prCyan("STEREO Camera **ML MODEL** initialization")
                self.SterCam_Model = YOLO_model_v1(model_path=StereoCamera_ModelPath)
        
        
        
        #-----------------------------        
        #Serial Communication to ESP32
        print(Back.CYAN+("="*24)+Style.RESET_ALL)
        prCyan("Serial Communication initialization")
        if self.RealSystem and self.Real[2]:
            self.SerialComms = Serial_Ard()
            if self.SerialComms.fail:
                prYellow("Switching to Fake Arduino")
                self.SerialComms = Serial_Ard_FAKE()
                self.Real[2]=False
        else: self.SerialComms = Serial_Ard_FAKE()

        
        
        
        
        #----------------------------- 
        print(Back.GREEN+("="*24)+Style.RESET_ALL)
        print(Back.GREEN+"PYTHON MAIN INIT COMPLETE"+Style.RESET_ALL)
        print(Back.GREEN+("="*24)+Style.RESET_ALL)
        
        
        #-----------------------------
        self.Forced=Forced
        self.MainProject_Loop()
        
        
    #---------------------------------------------------------------------
    def __del__(self):
        prALERT("Deleting PRIM_MAIN")
        os.system("pkill -f MS_startup.sh")
        if self.Real[2]: time.sleep(2)

        
        
    #---------------------------------------------------------------------
    def MainProject_Loop(self,Forced=False):
        #-----
        if self.Forced or Forced: prALERT("__WARNING__ Operating MainLoop in:\tFORCED")
        
        #-----
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
        self.Stereo_AngDep = None #Relative [Angle, Depth] - 2xN, 2D
        self.Stereo_RelPos = None #Relative [X, Y] - 2xN, 2D
        updated=True#False

        #-----
        Previous_State = 0
        Curr_State = 0
        Current_Cordinate = []  #use??????, is this a duplicate of Current_Location??
        Path=[]
        Path_Index = -2
        Current_Location = [0,0]
        Runway_Boundaries= []

        Trash_Collected_Locations = []  #use?????? set but not used, send to UI?
        Trash_Index = -1
        
        #====================================================================
        while True:
            #-----------
            #	get message if there is
            if self.Forced or Forced:
                #COLL	[40,100]
                send_mess = input("FORCE_SEND >")
                if len(send_mess)!=0: self.SerialComms.send_message(send_mess)
            message = self.SerialComms.read_message()
            if not(message is None):
                
                #==================================
                #print(message.split('\t'))
                #m=message.split('\t')[0]
                #prGreen(f"<{m}>")
                #print(message.split('\t')[0] == "STAR", (Curr_State == 0 or Curr_State == 2), message.split('\t')[0] == "STAR" and (Curr_State == 0 or Curr_State == 2))
            
                #--------------
                #printing
                prCyan(message)
                prPurple(f"Curr, Prev\t\t{Curr_State}, {Previous_State}",
                f"RunWayBound\t\t{Runway_Boundaries}",
                f"PathIdx, PathLen, PathTarg\t\t{Path_Index}, {len(Path)}, { f'[{Path[Path_Index][0]}, {Path[Path_Index][1]}]' if (Path is not None and Path_Index>=0) else None }",
                f"Current_Location\t\t{Current_Location}",
                f"currTrashTarg: Stereo_AngDep\t\t{Trash_Index}: {self.Stereo_AngDep if self.Stereo_AngDep is not None else None}",
                f"currTrashTarg: Stereo_RelPos\t\t{Trash_Index}: {self.Stereo_RelPos if self.Stereo_RelPos is not None else None}",
                f"Tele Angles:\t\t{Trash_Index}: {self.Tele_angles}",sep='\n')

            
            
                #==================================
                #STOP STATE 
                if message == "STOP":
                    prALERT("Entered Stop")
                    #raise RuntimeError("STOPPING PRIMARY JETSON MAIN: STOP MESSAGE")
                    #-----
                    #Resetting
                    self.Tele_angles = None #Relative Angles - 1xN, 1D
                    self.Stereo_AngDep = None #Relative [Angle, Depth] - 2xN, 2D
                    self.Stereo_RelPos = None #Relative [X, Y] - 2xN, 2D
                    Previous_State = 0
                    Curr_State = 0;updated=True
                    Current_Cordinate = []  #use??????, is this a duplicate of Current_Location??
                    Path=[]
                    Path_Index = -2
                    Current_Location = [0,0]
                    Runway_Boundaries= []
                    Trash_Collected_Locations = []  #use?????? set but not used, send to UI?
                    Trash_Index = -1
                    #-----
                    while True:
                        message = self.SerialComms.read_message()
                        if message is None: continue
                        if message.split('\t')[0] == "STAR":
                            for ele in message.split('\t')[1].strip().split(':'):
                                #print(ele)
                                x, y = map(float, ele.split(','))
                                Runway_Boundaries.append((x, y))
                            Previous_State = Curr_State
                            Curr_State = 1;updated=True
                            prALERT(">>RESUME PRIMARY JETSON MAIN")
                            break
                        elif not message is None: prRed(f"Incoming Message but not 'STAR' to restart:\t{message}")
                #==================================
                
                
                #-----
                if message == "ESTO" :
                    print("Estop Triggered")
            
                #PAUSE STATE (2)
                elif message == "PAUS":
                    Previous_State = Curr_State
                    Curr_State = 2;updated=True #not necessairy but for redundancy
                    prALERT("PAUSING PRIMARY JETSON MAIN: PAUSE MESSAGE")
                    while True:                    
                        message = self.SerialComms.read_message()
                        if message == "PAUS":
                            prALERT("RESUME PRIMARY JETSON MAIN")
                            Curr_State = Previous_State;updated=True
                            Previous_State = 2
                            break
                        elif not message is None: prRed(f"Incoming Message but not 'PAUS' to unpause:\t{message}")
                
                
                
                
                #====================================================================
                #### Update location -- not a state
                #structure: 'CPOS\t[  4 floating point values  ]
                #   ex (do own tab):   CPOS\t[3, 12]
                elif message.split('\t')[0] == "CPOS":
                    Current_Location = [ float(ele) for ele in message.split('\t')[1][1:-1].split(',') ]

                ### START STATE ###
                #structure: 'STAR\t[  4 floating point values  ]
                #   ex (do own tab):   STAR\t[(p1,p2,p3)
                elif message.split('\t')[0] == "STAR" and (Curr_State == 0 or Curr_State == 2) :
                    #print(message.split('\t')[1])
                    #print(message.split('\t')[1].strip())
                    #print(message.split('\t')[1].strip().split(':'))
                    for ele in message.split('\t')[1].strip().split(':'):
                        #print(ele)
                        x, y = map(float, ele.split(','))
                        Runway_Boundaries.append((x, y))

                    Previous_State = Curr_State
                    Curr_State = 1;updated=True
            
                ### WAITING FOR APPROVAL STATE
                elif message == "OKAY" and Curr_State == 5 :
                    Previous_State = Curr_State
                    Curr_State = 6;updated=True
    
                elif message == "NKAY" and Curr_State == 5 : #Object Located (waiting)
                    #original point state, goes to next point in path
                    # Previous_State = Curr_State
                    # Curr_State = 6;updated=True
                    Path_Index+=1

                ### Waiting to arrive at precise location state (STATE 7)
                elif message.split('\t')[0] == "ARSR" and Curr_State == 7:
                    Current_Location = [ float(ele) for ele in message.split('\t')[1][1:-1].split(',') ]
                    self.SerialComms.Bluetooth("To bluetooth : Trash Picked Up")
                    # self.SerialComms.Search_GoTo("Return to this cord") #NOTE Is this not handled by other comms from other states???? Is this Search??
                    Previous_State = Curr_State
                    Curr_State = 8;updated=True
            
                #TAKE PICTURE AND SAVE to folder
                elif ( message == "CAMR" and self.Real[0] and self.Real[1]):
                    prYellow(f"taking your picture ;)\t\t<{not self.SterCam is None}, {not self.TeleCam is None}>")
                    dstr=datestr()
                    if not self.SterCam is None: cv2.imwrite(f"DataCollect/Stereo/STER__{dstr}.jpg",     self.SterCam.get_feed())
                    if not self.TeleCam is None: cv2.imwrite(f"DataCollect/Telescopic/TELE__{dstr}.jpg", self.TeleCam.get_feed())
            

                
            #==============
            # 0 - READY TO START
            if Curr_State == 0:
                if updated: prLightPurple(f"EXEC State {Curr_State}");updated=False
                #------
                continue
            
            #==============
            # 1 - START
            elif(Curr_State == 1):
                if updated: prLightPurple(f"EXEC State {Curr_State}");updated=False
                #------
                prYellow("Generating Path")
                Path = generate_path(Runway_Boundaries[0],Runway_Boundaries[1],Runway_Boundaries[2])
                prGreen("Path Generated")
                #self.SerialComms.Collect_GoTo([10,1])    #TEST!!!!!!!
                
                Path_Index = -1
                Previous_State = 1
                Curr_State = 3;updated=True
            
            #==============
            #State 2 is pause
            
            #==============
            # 3 - Go to Next Path Index
            elif(Curr_State == 3):
                if updated: prLightPurple(f"EXEC State {Curr_State}");updated=False
                #------
                #edge case, try to travel with no path
                if(Path_Index == -2):
                    Curr_State = 0;updated=True
                else :
                    Path_Index += 1
                    # prRed(f'{Current_Location}, {Path[Path_Index]}')
                    # prRed(f'{Current_Location[0]}, {Path[Path_Index][0]}')
                    # prRed(f'{Current_Location[1]}, {Path[Path_Index][1]}')
                    if(Path_Index > len(Path)-1):
                        Path_Index = -2
                        Curr_State = 0;updated=True
                    elif (Current_Location[0] == Path[Path_Index][0]) or (Current_Location[1] == Path[Path_Index][1] and not(Path_Index < 0) ):
                        Curr_State = 4;updated=True
                    else:
                        Curr_State = 3;updated=True
                Previous_State = 3
                
                #add go to command 
            
            #==============
            # 4 - Detect Objects
            elif(Curr_State == 4):
                if updated: prLightPurple(f"EXEC State {Curr_State}");updated=False
                #------
                #TODO: SOMEWHERE HERE go to self.Tele_angles[ang_ind]
                    
                if Previous_State != 4: start_time = time.time()
                if self.detect_Tele(): 
                    Curr_State = 5;updated=True
                    #tell bluetooth about objec
                    #NOTE : possible pickup the same object over and over BUGGG
                    #add message
                    self.SerialComms.Bluetooth(  str(self.Tele_angles[0])  )
                elif (time.time() - start_time) > 60: Curr_State = 3;updated=True # go to next point, nothing is detected here
                else: Curr_State = 4;updated=True
                Previous_State = 4
            
            #==============
            # 5 - Object Located (Notify Officals)
            elif(Curr_State == 5):
                if updated: prLightPurple(f"EXEC State {Curr_State}:  <waiting for approval>");updated=False
                #------
                #Dead state while waiting for officals
                Previous_State = 5
            
            #==============
            # 6 - Drive to Object (relative, then precise)
            elif(Curr_State == 6):
                if updated: prLightPurple(f"EXEC State {Curr_State}");updated=False
                #------
                ### TODO @Jonah add in ur piece to this
                #Will stay in this state until there is a precise location found or object is lost
                #precise location: Stereo Camera
                #send tele message
                self.SerialComms.AngDrive_GoTo(self.Tele_angles[0])
                if not(Previous_State == 6): start_time = time.time()
                if self.detect_Stereo():
                    Curr_State = 7;updated=True
                    self.SerialComms.Collect_GoTo(  str(self.Stereo_AngDep[0])  )
                elif (time.time() - start_time) > 60:
            	    Curr_State = 3;updated=True # go to next point, nothing is detected her)
            	    self.SerialComms.Bluetooth("OBJT")
                else:
                    #object is still searching
                    Curr_State = 6;updated=True
                Previous_State = 6
            
            #==============
            # 7 - Wait until trash is collected
            elif(Curr_State == 7):
                if updated: prLightPurple(f"EXEC State {Curr_State}");updated=False
                # will stay in this state until we are at set locations
                if pntDist(Current_Location,self.Stereo_RelPos[0])<=0.03: #NOTE: within 3cm
                    Trash_Collected_Locations.append(Current_Location)
                    Curr_State = 9;updated=True
                else:  Curr_State = 7;updated=True
                Previous_State = 7
            
            #==============
            # 9 - Return to Path Cord
            elif(Curr_State == 9):
                if updated: prLightPurple(f"EXEC State {Curr_State}");updated=False
                #will stay in this stay in this state until cordinates are reached
                if (Current_Location[0] == Path[Path_Index][0]) or (Current_Location[1] == Path[Path_Index][1]):
                    Curr_State = 4;updated=True
                else :
                    Curr_State = 9;updated=True
                Previous_State = 9
            
            
            #-------------------
            #printing
            #prLightPurple("***AFTER****",
            #f"Curr, Prev\t\t{Curr_State}, {Previous_State}",
            #f"RunWayBound\t\t{Runway_Boundaries}",
            #f"PathIdx, PathLen, PathTarg\t\t{Path_Index}, {len(Path)}, { f'[{Path[Path_Index][0]}, {Path[Path_Index][1]}]' if (Path is not None and Path_Index>=0) else None }",
            #f"Current_Location\t\t{Current_Location}",
            #f"currTrashTarg: Stereo_AngDep\t\t{Trash_Index}: {self.Stereo_AngDep if self.Stereo_AngDep is not None else None}",
            #f"currTrashTarg: Stereo_RelPos\t\t{Trash_Index}: {self.Stereo_RelPos if self.Stereo_RelPos is not None else None}",
            #f"Tele Angles:\t\t{Trash_Index}: {self.Tele_angles}",sep="\n")
                
               
        
    def detect_Tele(self):
        #check telescopic camera for objects and their relative Angle
        if self.Real[0]:
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
        if self.Real[1]:
            Stereo_photo = self.SterCam.get_feed()
            Stereo_results = self.SterCam_Model.run_model( Stereo_photo  )
            if Stereo_results is not None:
                self.Stereo_AngDep = [ self.SterCam.get_relativeAngDep( find_center(res[1]) ) for res in Stereo_results ] #list of relative positions of tras
                self.Stereo_RelPos = [ self.SterCam.get_relativePOSITION( find_center(res[1]) ) for res in Stereo_results ] #list of relative positions of trashh
                #outputs cropped & compressed pictures of trash
                if save_image:
                    for index,res in enumerate(Stereo_results):
                        reduce_ImgObj( img= Stereo_photo,
                                       coords=find_center(res[1]),
                                       output_path=f"{CROPCOMPR_FILEPATH}{res[0]}_{index}___{goodtime()}" )
                return True
            else:
                self.Stereo_AngDep = None
                self.Stereo_RelPos = None
                return False
        else:
            if input('>S>>')=='y':
                self.Stereo_AngDep = [   [6,12], [3,12]   ] #NOTE: change??
                self.Stereo_RelPos = [   [6,12], [11.93, 1.25]   ] #NOTE: change??
                return True
            else:
                self.Stereo_AngDep = None
                self.Stereo_RelPos = None
                return False



prGreen("PRIMARY MAIN Jetson: Class Definition Success")
#===============================================================================



if __name__ == "__main__":
    try:
        eevee = PRIM_Main_Jetson(Real=[False,False,True])#,Forced=True)
    except Exception as e:
        os.system("pkill -f MS_startup.sh")
        raise RuntimeError("PRIM Jetson __main__ Error") from e
    
    
