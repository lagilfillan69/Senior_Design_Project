# Written by Jonah Earl Belback

# Stable container for Depth Camera from Carnegie Robotics

import math, platform, subprocess,os,time

#ROS
import rclpy, threading
from rclpy.node import Node
from sensor_msgs.msg import Image

#Other Module Imports
try:
    from helper_functions import *
    from Camera_Node import DisparitySubscriber,ColorImgSubscriber
    from SD_constants import STEREOCAM_GND_HEIGHT,STEREOCAM_HORZ_DEG_VIEW,STEREOCAM_VERT_DEG_VIEW#needs to be manually set
except:
    from Py_Modules.helper_functions import *
    from Py_Modules.Camera_Node import DisparitySubscriber,ColorImgSubscriber
    from Py_Modules.SD_constants import STEREOCAM_GND_HEIGHT,STEREOCAM_HORZ_DEG_VIEW,STEREOCAM_VERT_DEG_VIEW#needs to be manually set




class Stereo_Camera:
    def __init__(self, IP_address=None, Port=None,
                 GND_Height=STEREOCAM_GND_HEIGHT,
                 H_DegView=STEREOCAM_HORZ_DEG_VIEW,
                 V_DegView=STEREOCAM_VERT_DEG_VIEW,
                 Real=True):
        self.IP_address = None
        self.port = None
        self.Depth_Map = None
        self.GND_Height = GND_Height
        self.H_DegView = H_DegView
        self.V_DegView = V_DegView
        if platform.system() != 'Linux': self.Real=False
        else: self.Real=Real
        
        #Start up Depth Camera; also boots Ros subscribers
        if self.Real:
            #Start up Depth Camera; also boots Ros subscribers
            self.establish_connection()
            print(Back.GREEN+"SUCCESS: ROS ESTABLISHED"+Style.RESET_ALL)
            #get shape
            t_frame = self.get_feed()
            self.height,self.width,self.layers = t_frame.shape
        else:
            prRed("Not real StereoCam, so don't expect ROS")
            self.height,self.width,self.layers = 1188,1920,3
        prLightPurple(f'DEPTH CAM:\t<{self.width}> w,  <{self.height}> h,  <{self.layers}> layers')
        print(Back.GREEN+"SUCCESS: DEPTH CAMERA INIT PASS"+Style.RESET_ALL)
        pass
    
    #---------------------------------------------------------------------
        
    def __del__(self):
        prALERT(f'Stereo_Camera Destructor:\tKilling ROS Node\n{"="*12}')
        if not self.Disparity_sub is None: self.Disparity_sub.destroy_node()
        if not self.ColorImg_sub is None: self.ColorImg_sub.destroy_node()
        rclpy.shutdown()
        prALERT("ROS Killed")
    
    #---------------------------------------------------------------------
    
    #start up Stereo Camera
    #start ROS
    def establish_connection(self):
        self.Disparity_sub = None
        self.ColorImg_sub = None
        if self.Real:
            '''
            cd
            cd ros2_ws
            source /opt/ros/humble/setup.bash
            source install/setup.bash
            ros2 launch multisense_ros multisense_language.py
            '''
            #NOTE: !!!!!!!!!!!! MAY need to edit the FILEPATH to shell script
            result = subprocess.call(['sh', './Py_Modules/MS_startup.sh'])
            time.sleep(1)
            if result !=0: raise KeyError(f"Could not establish connection\tresult: {result}")
            
            #Start up ROS
            rclpy.init()
            # self.Disparity_sub = self.create_subscription(sensor_msgs.msg.Image, '/multisense/left/disparity', self.callback1, 10, Relability="keep last")
            # self.ColorImg_sub = self.create_subscription(sensor_msgs.msg.Image, '/multisense/left/image_color', self.callback2, 10, Relability="keep last")
            self.Disparity_sub = DisparitySubscriber()
            self.ColorImg_sub = ColorImgSubscriber()
            # rclpy.spin_once(self.Disparity_sub, timeout_sec=0.01)
            # rclpy.spin_once(self.ColorImg_sub, timeout_sec=0.01)
            self.check_connection_DISPAR()
            self.check_connection_CLRIMG()
            
            return result == 0
    
    #return T/F if able to connect
    #Both Connections
    def check_connection(self):
        #get current last update times        
        time_dis= self.Disparity_sub.lastupdate
        time_img= self.ColorImg_sub.lastupdate
        rclpy.spin_once(self.Disparity_sub, timeout_sec=0.01)
        rclpy.spin_once(self.ColorImg_sub, timeout_sec=0.01)
        return (time_dis!=self.Disparity_sub.lastupdate) and (time_img!=self.ColorImg_sub.lastupdate)
    
    #return T/F if able to connect
    #also spins the node once
    #!!!! Use this to update the node, then extract Node.want
    def check_connection_DISPAR(self):
        #get current last update times
        time_chk= self.Disparity_sub.lastupdate
        rclpy.spin_once(self.Disparity_sub, timeout_sec=0.01)
        if (time_chk==self.Disparity_sub.lastupdate): raise KeyError("Disparity_sub:\tCould not check connection")
    
    #return T/F if able to connect
    #also spins the node once
    #!!!! Use this to update the node, then extract Node.want
    def check_connection_CLRIMG(self):
        #get current last update time
        time_chk= self.ColorImg_sub.lastupdate
        rclpy.spin_once(self.ColorImg_sub, timeout_sec=0.01)
        if (time_chk==self.ColorImg_sub.lastupdate): raise KeyError("ColorImg_sub:\tCould not check connection")
    
    
    #---------------------------------------------------------------------
    
    #return camera feed (colored rectified image)
    def get_feed(self,new=True):
        if new: self.check_connection_CLRIMG() #update
        return self.ColorImg_sub.want
    
    #helper func for get_relativePOSITION and get_size
    def get_depthPOINT(self, coordX, coordY, new=True):
        if new: self.check_connection_DISPAR() #update
        return self.Disparity_sub.want[coordX, coordY]
    
    
    #---------------------------------------------------------------------
    
    #helper func for get_relativePOSITION and get_size
    #pos: angle to the right
    #neg: angle to the left
    def get_relativeANGLEX(self, coord):
        mid = self.width/2
        diff = mid - coord
        
        #left
        if diff>0: return -abs(diff) * self.H_DegView/self.width
        #right
        elif diff<0: return abs(diff) * self.H_DegView/self.width
        #middle
        else: return 0
    
    #Not sure if we'll use
    def get_relativeANGLEY(self, coord):
        mid = self.height/2
        diff = mid - coord
        
        #left
        if diff>0: return -abs(diff) * self.V_DegView/self.height
        #right
        elif diff<0: return abs(diff) * self.V_DegView/self.height
        #middle
        else: return 0
    
    
    #=====================================================================
    
    #get relative position in COORDINATES given a point from center of bounding box from the YOLO Model
    def get_relativePOSITION(self, coord):
        
        #current postiion is [0,0]
        #telling how far it is from the robots current position
        
        angle = self.get_relativeANGLEX(coord[0])
        depth = self.get_depthPOINT(coord[0],coord[1])
        
        distance = math.sqrt(   depth**2 - self.GND_Height**2   )
        
        if angle == 0: return [distance,0]
        else:
            x_dist = distance * math.sin(math.radians(angle))
            y_dist = math.sqrt(   distance**2 - x_dist**2   )#distance * math.cos(angle)
            return [x_dist,y_dist]
        
    #realtive position with current angle and current position
    def get_relativePOSITION(self, coord, currPOS, currANG):
        
        angle = self.get_relativeANGLEX(coord) + currANG
        depth = self.get_depthPOINT(coord[0],coord[1])
        
        distance = math.sqrt(   depth**2 - self.GND_Height**2   )
        
        if angle == 0: return [currPOS[0]+distance,   currPOS[1]]
        else:
            x_dist = distance * math.sin(math.radians(angle))
            y_dist = math.sqrt(   distance**2 - x_dist**2   )#distance * math.cos(angle)
            return [x_dist,y_dist]
    
    #=====================================================================
    
    def get_size(self, BB_coords):
        #BB_cord: [   [cord of Top Left bounding box point], [cord of Bottom Right]   ]
        TL_cord = self.get_relativePOSITION(BB_coords[0][0],BB_coords[0][1])#x of top left;     y of top left
        TR_cord = self.get_relativePOSITION(BB_coords[0][0],BB_coords[1][1])#x of top left;     y of bot right
        BL_cord = self.get_relativePOSITION(BB_coords[1][0],BB_coords[0][1])#x of bot right;    y of top left
        BR_cord = self.get_relativePOSITION(BB_coords[1][0],BB_coords[1][1])#x of bot right;    y of bot right
        
        #calculate area for general quadrilateral
        a = math.sqrt(   (TL_cord[0]-TR_cord[0])**2  +  (TL_cord[1]-TR_cord[1])**2   ) #distance from TL to TR
        b = math.sqrt(   (TR_cord[0]-BR_cord[0])**2  +  (TR_cord[1]-BR_cord[1])**2   ) #distance from TR to BR
        c = math.sqrt(   (BR_cord[0]-BL_cord[0])**2  +  (BR_cord[1]-BL_cord[1])**2   ) #distance from BR to BL
        d = math.sqrt(   (BL_cord[0]-TL_cord[0])**2  +  (BL_cord[1]-TL_cord[1])**2   ) #distance from BL to TL
        semiperimeter = (a+b+c+d)/2
        
        return math.sqrt(
                    (semiperimeter - a) *
                    (semiperimeter - b) *
                    (semiperimeter - c) * 
                    (semiperimeter - d)
                    )



prGreen("Stereo_Camera: Class Definition Success")
#===============================================================================



if __name__ == "__main__":
    pass