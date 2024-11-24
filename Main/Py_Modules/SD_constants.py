# Written by Jonah Earl Belback

'''
Keeper of Constant variables
'''
import os
dir_path = os.path.abspath("").replace('\\','/')
print(f"CONSTANTS DIRECTORY:\t\t<{dir_path}>")


#=========================
#STEREO CAMERA
STEREOCAM_GND_HEIGHT = 8 #8" !!!!!!!!!!!!!!!!! UNITS
STEREOCAM_HORZ_DEG_VIEW = 135 #https://www.carnegierobotics.com/AutonomousVehicles/CameraManufacturing/StereoCameraManufacturing/KS21i/Files/KS21i_Data_Sheet_CRL.pdf
STEREOCAM_VERT_DEG_VIEW = 84
FXTX=126.1172

#TELESCOPIC CAMERA
TELECAM_PORT=0
TELECAM_GND_HEIGHT = 13.25 #13.25" rn?	!!!!!!!!!!!!!!!!!!!! UNITS
TELECAM_FOCAL_LENGTH =  135# 18mm shortest, 135 highest zoom



#=========================
#SERIAL COMMUNICATIONS
import platform
if platform.system() == 'Linux': COM_PORT="/dev/ttyACM0"
else: COM_PORT="COM3"
BAUDRATE=9600



#=========================
models_path=dir_path+"/Py_Modules/YOLOv8/loadable_models/"
#MODELSHOW OFF
DEMO_STEREOCAM_MODELPATH = models_path+"DEMO_1920x1188.pt" #NOTE: NEEDS ACTUALLY SET
DEMO_TELECAM_MODELPATH = models_path+"DEMO_1920x1188.pt" #NOTE: NEEDS ACTUALLY SET

#MAIN
STEREOCAM_MODELPATH = models_path+"" #NOTE: NEEDS ACTUALLY SET
TELECAM_MODELPATH = models_path+"" #NOTE: NEEDS ACTUALLY SET
CROPCOMPR_FILEPATH = "" #NOTE: NEEDS ACTUALLY SET #end with '/'
if STEREOCAM_MODELPATH[-3:] != '.pt': STEREOCAM_MODELPATH = DEMO_STEREOCAM_MODELPATH
if TELECAM_MODELPATH[-3:]   != '.pt': TELECAM_MODELPATH = DEMO_TELECAM_MODELPATH



#=========================
#PATH PLANNING
#Max seeing distance of the bot in height and width in meters
PP_RANGE_WIDTH = 10.0
PP_RANGE_HEIGHT= 10.0 
PP_START = [0,0]
