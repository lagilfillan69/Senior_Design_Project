# Written by Jonah Earl Belback

# Stable container for Depth Camera from Carnegie Robotics

import math

try:
    from helper_functions import *
    from SD_constants import STEREOCAM_GND_HEIGHT,STEREOCAM_HORZ_DEG_VIEW,STEREOCAM_VERT_DEG_VIEW#needs to be manually set
except:
    from Py_Modules.helper_functions import *
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
        self.Real=Real
        
        if self.Real:
            if not  self.establish_connection(): raise KeyError("Could not establish connection")
            if not self.check_connection(): raise KeyError("Could not check connection")
        
        #get shape
        if self.Real:
            t_frame = self.get_feed()
            self.height,self.width,self.layers = t_frame.shape
        else: self.height,self.width,self.layers = 1188,1920,3
        prLightPurple(f'DEPTH CAM:\t<{self.width}> w,  <{self.height}> h,  <{self.layers}> layers')
        print(Back.GREEN+"SUCCESS: DEPTH CAMERA INIT PASS"+Style.RESET_ALL)
        pass
    
    #---------------------------------------------------------------------
    
    def establish_connection(self):
        #return T/F if able to connect
        #NOTE: need actual functionality to figure out
        return False
    
    def check_connection(self):
        #return T/F if able to connect
        #NOTE: need actual functionality to figure out
        return False
    
    
    #---------------------------------------------------------------------
    
    #return camera feed
    def get_feed(self):
        #return camera feed
        if self.Real and not self.check_connection(): raise KeyError("Could not check connection")
        #NOTE: need actual functionality to figure out
        pass
    
    #set internal object
    def get_depthmap(self):
        if self.Real and not self.check_connection(): raise KeyError("Could not check connection")
        #NOTE: need actual functionality to figure out
        self.Depth_Map = None
        pass
    
    
    #---------------------------------------------------------------------
    
    #helper func for get_relativePOSITION and get_size
    def get_depthPOINT(self, coord):
        #NOTE: need actual functionality to figure out
        self.get_depthmap()
        pass
    
    
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