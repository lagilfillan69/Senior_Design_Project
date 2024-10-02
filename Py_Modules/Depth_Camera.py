# Written by Jonah Earl Belback

# Stable container for Depth Camera from Carnegie Robotics

import math
from fun_colors import *
from SD_constants import DEPTHCAM_GND_HEIGHT,DEPTHCAM_DEGREE_VIEW


class Depth_Camera:
    def __init__(self, IP_address=None, Port=None, GND_Height=DEPTHCAM_GND_HEIGHT, Degree_View=DEPTHCAM_DEGREE_VIEW):
        self.IP_address = None
        self.port = None
        self.Depth_Map = None
        self.GND_Height = GND_Height
        self.Degree_View = Degree_View
        
        if not  self.establish_connection(): raise KeyError("Could not establish connection")
        if not self.check_connection(): raise KeyError("Could not check connection")
        
        #get shape
        t_frame = self.get_feed()
        self.height,self.width,self.layers = t_frame.shape
        prLightPurple(f'DEPTH CAM:\t<{self.width}> w,  <{self.height}> h,  <{self.layers}> layers')
        print(Back.GREEN+"SUCCESS: DEPTH CAMERA INIT PASS"+Style.RESET_ALL)
        pass
    
    def establish_connection(self):
        #return T/F if able to connect
        #NOTE: need actual functionality to figure out
        return False
    
    def check_connection(self):
        #return T/F if able to connect
        #NOTE: need actual functionality to figure out
        return False
    
    
    #---------------------------------------------------------------------
    
    def get_feed(self):
        #return camera feed
        pass
    
    def get_depthmap(self):
        #set internal object
        self.Depth_Map = None
        pass
    
    
    #---------------------------------------------------------------------
    #helper func for get_relativePOSITION and get_size
    def get_depthPOINT(self, coord):
        #NOTE: need actual functionality to figure out
        pass
    
    '''
    (%of screen from middle to end on x axis)*45?
    Left:  *=-1
    '''
    #helper func for get_relativePOSITION and get_size
    def get_relativeANGLE(self, coord):
        mid = self.width/2
        diff = mid - coord[0]
        
        #left
        if diff>0:
            return (1-(diff/mid)) * self.Degree_View/2
        #right
        elif diff<0:
            return (diff/mid) * self.Degree_View/2
        #middle
        else:
            return 0
    
    
    #=====================================================================
    
    #get relative position in COORDINATES given a point from center of bounding box from the YOLO Model
    def get_relativePOSITION(self, coord):
        
        #current postiion is [0,0]
        #telling how far it is from the robots current position
        
        angle = self.get_relativeANGLE(coord[0],coord[1])
        depth = self.get_depthPOINT(coord[0],coord[1])
        
        distance = math.sqrt(   depth**2 - self.GND_Height**2   )
        
        if angle == 0: return [distance,0]
        else:
            x_dist = distance * math.sin(angle)
            y_dist = distance * math.cos(angle)
            return [x_dist,y_dist]
        
    #realtive position with current angle and current position
    def get_relativePOSITION(self, coord, currPOS, currANG):
        
        angle = self.get_relativeANGLE(coord[0],coord[1]) + currANG
        depth = self.get_depthPOINT(coord[0],coord[1])
        
        distance = math.sqrt(   depth**2 - self.GND_Height**2   )
        
        if angle == 0: return [currPOS[0]+distance,   currPOS[1]]
        else:
            x_dist = distance * math.sin(angle)
            y_dist = distance * math.cos(angle)
            return [currPOS[0]+x_dist,   currPOS[1]+y_dist]
    
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