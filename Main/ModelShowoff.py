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



typeRun = input("Type of Run:\n1: Both Cameras\n2: Tele Only\n3: Stereo Only\n>>")
if typeRun=='': typeRun=1
else: typeRun=int(typeRun)
if typeRun>3 or typeRun<1: raise RuntimeError("Not within bounds")

#===============================================================================
if typeRun!=3:
    #Telescopic Camera
    print(Back.CYAN+("="*24)+Style.RESET_ALL)
    prCyan("TELESCOPIC Camera initialization")        
    TeleCamObj = TeleCAM()
    if TeleCamObj.fail:
        if typeRun==2: raise RuntimeError("Couldnt make TELE")
        if typeRun==1: typeRun=3
    else:
        #Telescopic YOLO Model
        prCyan("TELESCOPIC Camera **ML MODEL** initialization")
        TeleCam_Model = YOLO_model_v1(model_path=DEMO_TELECAM_MODELPATH)
        prGreen(f'TELE CLASS NAMES:\t{TeleCam_Model.model.names}')



#-----------------------------
if typeRun!=2:
    #Stereo Camera
    print(Back.CYAN+("="*24)+Style.RESET_ALL)
    prCyan("STEREO Camera initialization")
    SterCamObj = Stereo_Camera()
    if SterCamObj.fail:
        if typeRun==3: raise RuntimeError("Couldnt make STEREO")
        if typeRun==1: typeRun=3
    else:
        #Stereo YOLO Model
        prCyan("STEREO Camera **ML MODEL** initialization")
        SterCam_Model = YOLO_model_v1(model_path=DEMO_STEREOCAM_MODELPATH)
        prGreen(f'STEREO CLASS NAMES:\t{SterCam_Model.model.names}')

    def balance_numpy(arr):
        min_v=np.min(arr)
        max_v=np.max(arr)
        prYellow(f"min {min_v},\tmax {max_v}")
        if max_v-min_v != 0:  return (((arr.copy()-min_v)/(max_v-min_v))*255).astype(np.uint8)
        else:  return np.zeros(arr.shape).astype(np.uint8)
    
    

#===============================================================================
if typeRun==1: initsplit=1.15
if typeRun==2: initsplit=2
if typeRun==3: initsplit=1.5
spl=initsplit

while True:
    if cv2.waitKey(1) == ord('q'): break
    if cv2.waitKey(1) == ord('a'): spl-=initsplit*0.2
    if cv2.waitKey(1) == ord('d'): spl+=initsplit*0.2
    TELEclasses=[];STERclasses=[]
    TELEangs=None;STER_RELPOSs=None;STER_SIZEs=None;STER_DepAng=None
    #--
    prGreen('\n\n'+'-'*8)
    
    
    #---------------------
    #   TELESCOPIC
    if typeRun!=3:
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
        if typeRun==2: cv2.imshow('TeleCamera <q key to quit>',resizeFrame(TELE_img,spl)) #display
    
    
    

    #---------------------
    #   STEREO
    if typeRun!=2:
        STER_img=SterCamObj.get_feed()    
        STER_depth=balance_numpy(SterCamObj.Depth_Map)
        STERresults = SterCam_Model.run_model(STER_img)
        if len(STERresults)>0:
            #draw
            for res in STERresults:
                STERclasses.append(res[0])
                cv2.rectangle(STER_img,  [int(res[1][0][0]),int(res[1][0][1])],   [int(res[1][1][0]),int(res[1][1][1])]   ,(255, 0, 0),2) #blue
                cv2.rectangle(STER_depth,  [int(res[1][0][0]),int(res[1][0][1])],   [int(res[1][1][0]),int(res[1][1][1])]   ,255,2) #solid block

        
            #	relative position
            #prPurple(f'---')
            #STER_RELPOSs = [SterCamObj.get_relativePOSITION(find_center(res[1]))  for res in STERresults]
            STER_RELPOSs = [SterCamObj.get_relativePOSITION_BOX(res[1])  for res in STERresults]
            #	relative Ang,Dep
            #prPurple(f'---')
            STER_DepAng = [SterCamObj.get_relativeAngDep_BOX(res[1])  for res in STERresults]
            #	size
            #prPurple(f'---')
            #STER_SIZEs = [SterCamObj.get_size(res[1])  for res in STERresults]
            STER_SIZEs = [SterCamObj.get_sizeWEIGHED(res[1])  for res in STERresults]
        else:
            STER_RELPOSs=None
            STER_DepAng=None
            STER_SIZEs=None

        prPurple(f'StereoCam Rel_POS:\t\t{STER_RELPOSs}')
        prLightPurple(f'StereoCam STER_DepAng:\t\t{STER_DepAng}')
        print(f'StereoCam Sizes:  \t\t{STER_SIZEs}')
        #if typeRun==3: cv2.imshow('StereoCamera <q key to quit>',resizeFrame(STER_img,3)) #display
        #if typeRun==3: cv2.imshow("Depthmap <q key to quit>",resizeFrame(STER_depth,3))
        if typeRun==3: cv2.imshow("StereoCamera, Depthmap   q key to quit>",resizeFrame(comboImg([STER_img,STER_depth]),spl)  )
    
    
    if typeRun==1: cv2.imshow("TeleCamera, StereoCamera, Depthmap   <q key to quit>", resizeFrame(comboImg([TELE_img,STER_img,STER_depth]),spl)  )
    

    
    
    if typeRun!=3: prYellow(f'TELE Classes:\t{TELEclasses}')
    if typeRun!=2: prYellow(f'STER Classes:\t{STERclasses}')
    
    
