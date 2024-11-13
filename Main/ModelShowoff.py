# Written by Jonah Earl Belback

# Show off Models

import os,sys,platform,time,subprocess,cv2
dir_path = os.path.abspath("").replace('\\','/')
if __name__ == "__main__": print(f"DIRECTORY:\t\t<{dir_path}>")
sys.path.append(dir_path)

#------------------------
print(platform.system())
from Py_Modules.helper_functions import *
from Py_Modules.JEB382_YOLOv8 import YOLO_model_v1
from Py_Modules.Stereo_Camera import Stereo_Camera
from Py_Modules.Tele_Camera  import TeleCAM
from Py_Modules.SD_constants import STEREOCAM_MODELPATH,TELECAM_MODELPATH
prGreen("Model Showoff Jetson: Import Success")




#===============================================================================
#Telescopic Camera
print(Back.CYAN+("="*24)+Style.RESET_ALL)
prCyan("TELESCOPIC Camera initialization")        
TeleCamObj = TeleCAM()

#Telescopic YOLO Model
prCyan("TELESCOPIC Camera **ML MODEL** initialization")
TeleCam_Model = YOLO_model_v1(model_path=TELECAM_MODELPATH)



#-----------------------------
#Stereo Camera
print(Back.CYAN+("="*24)+Style.RESET_ALL)
prCyan("STEREO Camera initialization")
SterCamObj = Stereo_Camera()

#Telescopic YOLO Model
prCyan("STEREO Camera **ML MODEL** initialization")
SterCam_Model = YOLO_model_v1(model_path=STEREOCAM_MODELPATH)
        
        
        


#===============================================================================
while True:
    if cv2.waitKey(1) == ord('q'): break
    
    
    #---------------------
    #   TELESCOPIC
    TELE_img=TeleCamObj.get_feed()    
    TELEresults = TeleCam_Model.run_model(TELE_img)
    if len(TELEresults)>0:
        #draw
        for res in TELEresults: cv2.rectangle(TELE_img,res[1],(0, 255, 0),2) #green
        #relative angle
        TELEcenters= [find_center(res[1]) for res in TELEresults]
    else: TELEcenters=None
    cv2.imshow('TeleCamera',TELE_img) #display
    
    
    
    
    #---------------------
    #   STEREO
    STER_img=SterCamObj.get_feed()    
    STERresults = SterCam_Model.run_model(STER_img)
    if len(STERresults)>0:
        #draw
        for res in STERresults: cv2.rectangle(STER_img,res[1],(255, 0, 0),2) #blue
        
        #relative position, size
        STER_RELPOSs = [SterCamObj.get_relativePOSITION(find_center(res[1]))  for res in STERresults]
        STER_SIZEs = [SterCamObj.get_size(res[1])  for res in STERresults]
    else:
        STER_RELPOSs=None
        STER_SIZEs=None
    cv2.imshow('StereoCamera',STER_img) #display
    
    
    
    
    #---------------------
    prGreen('\n\n'+'-'*8)
    print(f'TeleCam RelAngles:\t\t{TELEcenters}')
    prLightPurple(f'StereoCam Rel_POS:\t\t{STER_RELPOSs}')
    print(f'StereoCam Sizes:  \t\t{STER_SIZEs}')
    
    
    