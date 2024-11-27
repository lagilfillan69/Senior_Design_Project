# Written by Jonah Earl Belback

'''
Keeper of Constant variables
'''
import os
from colorama import Back, Style
dir_path = os.path.abspath("").replace('\\','/')
print(f"CONSTANTS DIRECTORY:\t\t<{dir_path}>")


#=========================
#STEREO CAMERA
STEREOCAM_GND_HEIGHT = 0 #0.22	#METERS, 22cm
#https://www.carnegierobotics.com/AutonomousVehicles/CameraManufacturing/StereoCameraManufacturing/KS21i/Files/KS21i_Data_Sheet_CRL.pdf
STEREOCAM_HORZDEGVIEW_C = 137	#colored cam
STEREOCAM_VERTDEGVIEW_C = 83
STEREOCAM_HORZDEGVIEW_S = 135	#stereo cam
STEREOCAM_VERTDEGVIEW_S = 84
FXTX=126.1172
convs=[0.495436,19.50535]
CONVERSION=convs[1] #0.495436 meters, 19.50535 inches
CLR2DPR1=1.029   #scaling x value on colorFeed to Dispar Feed
CLR2DPR2=0.00007 #scaling x value on colorFeed to Dispar Feed
CLR2DPR3=-0.2566 #scaling x value on colorFeed to Dispar Feed
CLR2DPR4=0.0048  #scaling x value on colorFeed to Dispar Feed
if CONVERSION==convs[0]: print(Back.YELLOW+"Depth in ___METERS___"+Style.RESET_ALL)
if CONVERSION==convs[1]: print(Back.YELLOW+"Depth in ___INCHES___"+Style.RESET_ALL)
if STEREOCAM_GND_HEIGHT==0: print(Back.RED+'!'*60+"\nCONSTANTS WARNING:\t\tSTEREOCAM_GND_HEIGHT at 0, are you testing????\n"+'!'*60+Style.RESET_ALL)

#TELESCOPIC CAMERA
TELECAM_PORT=0
TELECAM_GND_HEIGHT = 0.36
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
DEMO_STEREOCAM_MODELPATH = models_path+"DEMO_1920x1188.pt"
DEMO_TELECAM_MODELPATH = models_path+"DEMO_1920x1188.pt"

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
