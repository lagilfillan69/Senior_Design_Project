# Written by Jonah Earl Belback

# Stable container for Depth Camera from Carnegie Robotics

import math, platform, subprocess,os,time,cv2,signal
import numpy as np

#ROS
#print( "wowza:", subprocess.run("bash -c 'source /opt/ros/humble/setup.bash'", shell=True) )
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
    def __init__(self,
                 GND_Height=STEREOCAM_GND_HEIGHT,
                 H_DegView=STEREOCAM_HORZ_DEG_VIEW,
                 V_DegView=STEREOCAM_VERT_DEG_VIEW,
                 Real=True,
                 multithread=True):
        self.Depth_Map = None
        self.GND_Height = GND_Height
        self.H_DegView = H_DegView
        self.V_DegView = V_DegView
        if platform.system() != 'Linux': self.Real=False
        else: self.Real=Real
        self.multithread = multithread and self.Real #only multithread if real and allowed
        
        #---------
        #Start up Depth Camera; also boots Ros subscribers
        self.CAMprocess=None; self.SpinThread=None #prevent minor error in destructor
        self.Disparity_sub=None; self.ColorImg_sub=None
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
            
        #---- end of class init   
        print(Back.GREEN+"SUCCESS: DEPTH CAMERA INIT PASS"+Style.RESET_ALL)
        
        
        #---------------------------
        '''
        try:
            self.init_helper()
        except Exception as e:
            prRed(f"Error starting 'Stereo_Camera', switch to Fake?:\ty?")
            if input(">").lower() == 'y':
                self.Real=False
                self.multithread = False
                self.init_helper()
            else: raise RuntimeError("Error loading Real Arduino") from e
        '''
            
            
    
    #---------------------------------------------------------------------
    def init_helper(self):
        #---------        
        #Start up Depth Camera; also boots Ros subscribers
        self.CAMprocess=None; self.SpinThread=None #prevent minor error in destructor
        self.Disparity_sub=None; self.ColorImg_sub=None
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
            
        #---- end of class init   
        print(Back.GREEN+"SUCCESS: DEPTH CAMERA INIT PASS"+Style.RESET_ALL)
        
        
           
    def __del__(self):
        #-------------
        #Parallel Terminal
        if not self.CAMprocess is None:
            prALERT(f'Stereo_Camera Destructor:\tKilling Camera Startup Parallel Terminal\n{"="*12}')
            try:
                prYellow("Giving time for Split terminal to run before closing")
                time.sleep(5)
                #os.kill(self.CAMprocess.pid,signal.SIGTERM)
                os.system("pkill -f MS_startup.sh")
                if self.CAMprocess.poll() is not None: prRed("Couldn't shutdown parallel terminal; please shutdown popped up terminal yourself if open")
            except Exception as e:
                prRed("error shutting down parallel terminal,Likely minor:\n",e)
        #-------------
        #Kill threads
        if self.multithread and not self.SpinThread is None:
            prALERT(f'Stereo_Camera Destructor:\tKilling Parallel Node Spin Threads\n{"="*12}')  
            try:
                #self.t1.raise_exception()
                #self.t2.raise_exception()
                self.KeepRunning = False
                prYellow("Giving time for Spin Thread to close")
                time.sleep(1)
                if self.SpinThread.is_alive(): self.SpinThread.raise_exception()
            except Exception as e:
                print("error shutting down parallel spin threads:",e)
        #-------------
        #Kill RCLPY
        prALERT(f'Stereo_Camera Destructor:\tKilling ROS Node\n{"="*12}')
        if not self.Disparity_sub is None: self.Disparity_sub.destroy_node()
        if not self.ColorImg_sub is None: self.ColorImg_sub.destroy_node()
        try:
            rclpy.shutdown()
        except Exception as e:
            raise RuntimeError(f"Error shutting down rclpy:\n{e}")
        prALERT("ROS Killed")
    
    #---------------------------------------------------------------------
    
    #start up Stereo Camera
    #start ROS
    def establish_connection(self):
        self.Disparity_sub = None
        self.ColorImg_sub = None
        if self.Real:
            '''
            cd ~/ros2_ws
            source /opt/ros/humble/setup.bash
            source /opt/ros/humble/setup.sh
            source install/setup.bash
            ros2 launch multisense_ros multisense_launch.py
            '''
            prYellow("Killing any missed parallel terminals for the ROS Camera Startup")
            os.system("pkill -f MS_startup.sh")
            #self.CAMprocess = subprocess.Popen(['x-terminal-emulator','-e', 'bash -c "./MS_startup.sh; exec bash"'],stderr=subprocess.PIPE)
            self.CAMprocess = subprocess.Popen(['x-terminal-emulator','-e', 'bash -c "~/MS_startup.sh; exec bash"'],stderr=subprocess.PIPE) #this should work from anywhere provided the shell file is in home
            prYellow("Loading parallel terminal to ---start up ROS CAMERA---")
            time.sleep(5)
            if self.CAMprocess.poll() is not None: raise RuntimeError(f"Could not establish connection to camera")
            
            #Start up ROS
            rclpy.init()
            self.Disparity_sub = DisparitySubscriber()
            self.ColorImg_sub = ColorImgSubscriber()
            # rclpy.spin_once(self.Disparity_sub, timeout_sec=0.01)
            # rclpy.spin_once(self.ColorImg_sub, timeout_sec=0.01)
            
            #---------        
            #Turning on ROS to multithread spin
            if self.multithread:
                prYellow("Starting ROS Subscriber threading")
                self.KeepRunning=True
                self.SpinThread = threading.Thread(target=self.helperSpinner)
                self.SpinThread.daemon = True
                #----
                self.SpinThread.start()
                prYellow("Giving Time for Spin Thread to Spin")
                time.sleep(5)
                
                #checking that it spun for a max of 5 seconds
                #once both have spun and gotten a msg at least once; exits
                st=time.time()
                while (self.Disparity_sub.first_try and self.ColorImg_sub.first_try):
                    if time.time()-st >5:
                        prYellow("Killing any missed parallel terminals for the ROS Camera Startup")
                        os.system("pkill -f MS_startup.sh")
                        raise RuntimeError("Could not establish connection;   SpinThread;   Timeout>5s")
                #----
                print(Back.GREEN+"SUCCESS: ROS THREADING PASS"+Style.RESET_ALL)
            
            
            self.check_connection_DISPAR()
            self.check_connection_COLIMG()
            
    #-----------
    #needed for threads to work, otherwises spins at the threads def
    #USING spin_once instead of rclpy.spin() to avoid unwanted opened instances outside this class
    #rclpy.spin() is secretly just spinning once a bunch anyway
    def helperSpinner(self):
        while self.KeepRunning:
            rclpy.spin_once(self.Disparity_sub, timeout_sec=0.01)
            rclpy.spin_once(self.ColorImg_sub, timeout_sec=0.01)
            self.Depth_Map = self.Disparity_sub.want
        prRed("Stereo_Camera;  from helperSpinner: Killing Spin Thread")
    #unused (problems)
    '''
    def helperSpin_DISPAR(self):       
        rclpy.spin(self.Disparity_sub)        
    def helperSpin_CLRIMG(self):       
        rclpy.spin(self.ColorImg_sub)
    '''
    
    
    #---------------------------------------------------------------------
    #return T/F if able to connect
    #also spins the node once
    #!!!! Use this to update the node, then extract Node.want
    def check_connection_DISPAR(self):
        if not self.multithread:
            #get current last update times
            time_chk= self.Disparity_sub.lastupdate
            rclpy.spin_once(self.Disparity_sub, timeout_sec=0.01)
            if (time_chk==self.Disparity_sub.lastupdate): raise RuntimeError("Disparity_sub:\tCould not check connection")
        else:
            #if self.t1.is_alive(): raise RuntimeError("Disparity_sub:\tCould not check connection;   Thread Dead")
            if not self.SpinThread.is_alive(): raise RuntimeError("SpinThread:\tCould not check connection;   Thread Dead")
            if abs(self.Disparity_sub.lastupdate-time.time())>2: raise RuntimeError("Could not check connection;   check_connection_DISPAR;   Timeout>2s")
    
    #return T/F if able to connect
    #also spins the node once
    #!!!! Use this to update the node, then extract Node.want
    def check_connection_COLIMG(self):
        if not self.multithread:
            #get current last update time
            time_chk= self.ColorImg_sub.lastupdate
            rclpy.spin_once(self.ColorImg_sub, timeout_sec=0.01)
            if (time_chk==self.ColorImg_sub.lastupdate): raise RuntimeError("ColorImg_sub:\tCould not check connection")
        else:
            #if self.t2.is_alive(): raise RuntimeError("ColorImg_sub:\tCould not check connection;   Thread Dead")
            if not self.SpinThread.is_alive(): raise RuntimeError("SpinThread:\tCould not check connection;   Thread Dead")
            if abs(self.ColorImg_sub.lastupdate-time.time())>2: raise RuntimeError("Could not check connection;   check_connection_COLIMG;   Timeout>2s")
    
    
    #---------------------------------------------------------------------
    
    #return camera feed (colored rectified image)
    def get_feed(self,new=True):
        if new or self.multithread: self.check_connection_COLIMG() #update
        if self.ColorImg_sub.want is None: raise RuntimeError("get_feed: self.ColorImg_sub.want is None")
        return self.ColorImg_sub.want
    
    #helper func for get_relativePOSITION and get_size
    def get_depthPOINT(self, coordX, coordY, new=True):
        if new or self.multithread: self.check_connection_DISPAR() #update
        if self.Disparity_sub.want is None: raise RuntimeError("get_depthPOINT: self.Disparity_sub.want is None")
        return self.Depth_Map[coordX, coordY]
    
    
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
    
    #get relative position in __Angle,Depth__ given a point from center of bounding box from the YOLO Model
    def get_relativeAngDep(self, coord):
        
        #current postiion is [0,0]
        #telling how far it is from the robots current position
        
        angle = self.get_relativeANGLEX(coord[0])
        depth = self.get_depthPOINT(coord[0],coord[1])
        distance = math.sqrt(   depth**2 - self.GND_Height**2   )
        
        return [angle,  distance]
        
    #realtive __Angle,Depth__ with current angle and current position
    def get_relativeAngDep(self, coord, currANG):
        
        angle = self.get_relativeANGLEX(coord) + currANG
        depth = self.get_depthPOINT(coord[0],coord[1])
        distance = math.sqrt(   depth**2 - self.GND_Height**2   )
        
        return [angle,  distance]
    
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
def balance_numpy(arr):
    min_v=np.min(arr)
    max_v=np.max(arr)
    if max_v-min_v != 0:  return (((arr.copy()-min_v)/(max_v-min_v))*255).astype(np.uint8)
    else:  return np.zeros(arr.shape).astype(np.uint8)
    




if __name__ == "__main__":
    try:
        cammie = Stereo_Camera()
    
        print("waiting (safe)...")
        time.sleep(4)
        print(f"wait done\n\n{'-'*24}\n")
    
        while True:
            cv2.imshow("Depthmap <q key to quit>",balance_numpy(cammie.Depth_Map))
            cv2.imshow("CameraFeed <q key to quit>",cammie.get_feed())
            if cv2.waitKey(1) == ord('q'): break    
    except Exception as e:
        print(e)
        os.system("pkill -f MS_startup.sh")


