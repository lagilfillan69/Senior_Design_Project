'''
Keeper of Constant variables
'''


#STEREO CAMERA
STEREOCAM_GND_HEIGHT = 0 #NOTE: NEEDS ACTUALLY SET
STEREOCAM_HORZ_DEG_VIEW = 135 #https://www.carnegierobotics.com/AutonomousVehicles/CameraManufacturing/StereoCameraManufacturing/KS21i/Files/KS21i_Data_Sheet_CRL.pdf
STEREOCAM_VERT_DEG_VIEW = 84

#TELESCOPIC CAMERA
TELECAM_PORT=0
TELECAM_GND_HEIGHT = 0 #13.25" rn?
TELECAM_FOCAL_LENGTH =  18# 18mm shortest, 135 highest zoom

#SERIAL COMMUNICATIONS
import platform
if platform.system() == 'Linux': COM_PORT="/dev/ttyACM0"
else: COM_PORT="COM3"
BAUDRATE=9600

#MAIN
STEREOCAM_MODELPATH = "" #NOTE: NEEDS ACTUALLY SET
TELECAM_MODELPATH = "" #NOTE: NEEDS ACTUALLY SET
CROPCOMPR_FILEPATH = "" #NOTE: NEEDS ACTUALLY SET #end with '/'

#PATH PLANNING
#Max seeing distance of the bot in height and width in meters
PP_RANGE_WIDTH = 10.0
PP_RANGE_HEIGHT= 10.0 
PP_START = [0,0]
