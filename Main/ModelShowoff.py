# Written by Jonah Earl Belback

# Show off Models
import numpy as np
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
from Py_Modules.SD_constants import STEREOCAM_MODELPATH,TELECAM_MODELPATH,DEMO_STEREOCAM_MODELPATH,DEMO_TELECAM_MODELPATH
prGreen("Model Showoff Jetson: Import Success")
prYellow(f'Tele Real:\t{TELECAM_MODELPATH}')
prYellow(f'Tele Fake:\t{DEMO_TELECAM_MODELPATH}')
prYellow(f'Stereo Real:\t{STEREOCAM_MODELPATH}')
prYellow(f'Stereo Fake:\t{DEMO_STEREOCAM_MODELPATH}')



#===============================================================================
#Telescopic Camera
print(Back.CYAN+("="*24)+Style.RESET_ALL)
prCyan("TELESCOPIC Camera initialization")        
TeleCamObj = TeleCAM()

#Telescopic YOLO Model
prCyan("TELESCOPIC Camera **ML MODEL** initialization")
TeleCam_Model = YOLO_model_v1(model_path=DEMO_TELECAM_MODELPATH)
class_names= TeleCam_Model.model.names
prGreen(f'CLASS NAMES:\t{class_names}')



#-----------------------------
#Stereo Camera
print(Back.CYAN+("="*24)+Style.RESET_ALL)
prCyan("STEREO Camera initialization")
SterCamObj = Stereo_Camera()

#Stereo YOLO Model
prCyan("STEREO Camera **ML MODEL** initialization")
SterCam_Model = YOLO_model_v1(model_path=DEMO_STEREOCAM_MODELPATH)

def balance_numpy(arr):
    min_v=np.min(arr)
    max_v=np.max(arr)
    if max_v-min_v != 0:  return (((arr.copy()-min_v)/(max_v-min_v))*255).astype(np.uint8)
    else:  return np.zeros(arr.shape).astype(np.uint8)
    
    
            
        


#===============================================================================
while True:
    if cv2.waitKey(1) == ord('q'): break
    TELEclasses=[];STERclasses=[]
    TELEangs=None;STER_RELPOSs=None;STER_SIZEs=None
    #--
    prGreen('\n\n'+'-'*8)
    
    
    #---------------------
    #   TELESCOPIC
    TELE_img=TeleCamObj.get_feed()    
    TELEresults = TeleCam_Model.run_model(TELE_img)
    if len(TELEresults)>0:
        #draw
        for res in TELEresults:
            TELEclasses.append(res[0])
            cv2.rectangle(TELE_img,  [int(res[1][0][0]),int(res[1][0][1])],   [int(res[1][1][0]),int(res[1][1][1])]   ,(0, 255, 0),2) #green
        #relative angle
        TELEangs= [TeleCamObj.get_relativeANGLEX(find_center(res[1])) for res in TELEresults]
    else: TELEangs=None
    
    prRed(f'TeleCam RelAngles:\t\t{TELEangs}')
    cv2.imshow('TeleCamera',TELE_img) #display
    
    
    
    '''
    #---------------------
    #   STEREO
    STER_img=SterCamObj.get_feed()    
    STER_depth=balance_numpy(SterCamObj.Depth_Map)
    STERresults = SterCam_Model.run_model(STER_img)
    if len(STERresults)>0:
        #draw
        for res in STERresults:
            STERclasses.append(res[0])
            cv2.rectangle(STER_img,  [int(res[1][0][0]),int(res[1][0][1])],   [int(res[1][1][0]),int(res[1][1][1])]   ,(255, 0, 0),2) #blue
            cv2.rectangle(STER_depth,  [int(res[1][0][0]),int(res[1][0][1])],   [int(res[1][1][0]),int(res[1][1][1])]   ,255,2) #solid block

        
        #relative position, size
        STER_RELPOSs = [SterCamObj.get_relativePOSITION(find_center(res[1]))  for res in STERresults]
        STER_SIZEs = [SterCamObj.get_size(res[1])  for res in STERresults]
    else:
        STER_RELPOSs=None
        STER_SIZEs=None

    prLightPurple(f'StereoCam Rel_POS:\t\t{STER_RELPOSs}')
    print(f'StereoCam Sizes:  \t\t{STER_SIZEs}')
    cv2.imshow('StereoCamera',STER_img) #display
    cv2.imshow("Depthmap <q key to quit>",STER_depth)
    '''
    
    
    prYellow(f'TELE Classes:\t{TELEclasses}')
    prYellow(f'STER Classes:\t{STERclasses}')
    
    
