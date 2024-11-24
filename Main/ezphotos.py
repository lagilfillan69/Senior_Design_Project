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
if TeleCamObj.fail: raise RuntimeError("Couldnt make TELE")



#-----------------------------
#Stereo Camera
print(Back.CYAN+("="*24)+Style.RESET_ALL)
prCyan("STEREO Camera initialization")
SterCamObj = Stereo_Camera()
if SterCamObj.fail: raise RuntimeError("Couldnt make STEREO")
def balance_numpy(arr):
    min_v=np.min(arr)
    max_v=np.max(arr)
    #prYellow(f"min {min_v},\tmax {max_v}")
    if max_v-min_v != 0:  return (((arr.copy()-min_v)/(max_v-min_v))*255).astype(np.uint8)
    else:  return np.zeros(arr.shape).astype(np.uint8)
    
    

#===============================================================================
#keyboard window scaling
from pynput import keyboard
global initsplit,spl,breker
initsplit=1.15
spl=initsplit
breker=False

def Regpress(key):
    try:
        global initsplit,spl
        if key == keyboard.Key.up: spl-=initsplit*0.2
        elif key == keyboard.Key.down: spl+=initsplit*0.2
        elif key == keyboard.Key.enter:
            global TELE_img, STER_img
            prYellow(f"taking your picture ;)",end='\t\t')
            dstr=datestr()
            cv2.imwrite(f"DataCollect/Stereo/STER__{dstr}.jpg",     STER_img)
            cv2.imwrite(f"DataCollect/Telescopic/TELE__{dstr}.jpg", TELE_img)
            cv2.imwrite(f"DataCollect/{dstr}.jpg", comboImg([TELE_img,STER_img]))
            prYellow('took!')
    except Exception as e:
        global breker
        breker=True
        prALERT(e)
    
def ESCpress(key):
    global breker
    if key == keyboard.Key.esc:
        breker=True
        return False
listenlearn = keyboard.Listener(on_press=Regpress, on_release=ESCpress)
listenlearn.start()



#===============================================================================
global TELE_img, STER_img
while True:
    if cv2.waitKey(1) == ord('q') or breker: break
    TELE_img=TeleCamObj.get_feed()
    STER_img=SterCamObj.get_feed()    
    cv2.imshow("TeleCamera, StereoCamera, Depthmap   <q key to quit>", resizeFrame(comboImg([TELE_img,STER_img]),spl)  )
    
listenlearn.join()
