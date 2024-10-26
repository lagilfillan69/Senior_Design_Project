# Written by Jonah Earl Belback

# Helper functions

import win32api,datetime,pandas
from colorama import Fore, Back, Style
def prRed(skk): print("\033[91m{}\033[00m" .format(skk))
def prGreen(skk): print("\033[92m{}\033[00m" .format(skk))
def prYellow(skk): print("\033[93m{}\033[00m" .format(skk))
def prLightPurple(skk): print("\033[94m{}\033[00m" .format(skk))
def prPurple(skk): print("\033[95m{}\033[00m" .format(skk))
def prCyan(skk): print("\033[96m{}\033[00m" .format(skk))
def prLightGray(skk): print("\033[97m{}\033[00m" .format(skk))
def prBlack(skk): print("\033[98m{}\033[00m" .format(skk))


#logging, graphing
def prALERT(skk):print(Back.RED+skk+Style.RESET_ALL)
def gdFL(fl): return f"{'{:.2f}'.format(float( fl ))}"

def logger(filepath,text):
    file = open(filepath,'a', encoding="utf-8")
    file.write(text+"\n")
    file.close()

DRIVENAME = "SURG24-ML_DATA"
def getDrive(drivename=DRIVENAME):
    drives = win32api.GetLogicalDriveStrings()
    dx = [x for x in drives.split("\000") if x]
    for drive in dx:
        try:
            #print(drive, win32api.GetVolumeInformation(drive))
            if drivename == str(win32api.GetVolumeInformation(drive)[0]): return str(drive)
        except: pass
    return None

def goodtime(tim):
    str=""
    if tim>86400: str+=f"{int(tim/86400)}d "; tim=tim%86400
    if tim>3600: str+=f"{int(tim/3600)}h "; tim=tim%3600
    if tim>60: str+=f"{int(tim/60)}m "; tim=tim%60
    str+= gdFL(tim)+"s"
    return str

#if file doesnt exist, make it. otherwise dont effect it
def file_helper(path):
    t_file= open(path,'a', encoding="utf-8")
    t_file.close()

def file_wipe(path):
    t_file= open(path,'w', encoding="utf-8")
    t_file.close()

def rgb(minimum, maximum, value):
    ratio = 2 * (value-minimum) / (maximum - minimum)
    b = max(0, (1 - ratio))
    r = max(0, (ratio - 1))
    g = 1-b-r
    return (r, g, b)

def datestr():
    return f'{datetime.datetime.now().date()}_{datetime.datetime.now().hour}_{datetime.datetime.now().minute}'

def mean(arr):
    tot=0
    for i in arr:tot+=i
    return tot/len(arr)

       
#===================
import cv2

def reduce_found_obj(file_path, coords, output_path, Expan_rate=0.3, Compress_rate=10):
    Expan_rate=1-Expan_rate
    #read
    img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    
    #crop
    img = img[ int(coords[0][1]*Expan_rate):int( img.shape[0]-(img.shape[0]-coords[1][1])*Expan_rate ),  int(coords[0][0]*Expan_rate):int( img.shape[1]-(img.shape[1]-coords[1][0])*Expan_rate )  ]
    
    #compress
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), Compress_rate]
    _, encimg = cv2.imencode('.jpg', img, encode_param)
    decoded_img = cv2.imdecode(encimg, cv2.IMREAD_GRAYSCALE)
    
    cv2.imwrite(output_path, decoded_img )

#coords= [ [x1y1],[x2,y2] ]
def find_center(coords):
    return [     abs(coords[0][0]-coords[1][0]),  abs(coords[0][1]-coords[1][1])      ]




import math
def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on Earth."""
    R = 6371000  # Earth radius in meters
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def gps_to_xy(lat1, lon1, lat2, lon2):
    """Convert GPS coordinates to local Cartesian coordinates using equirectangular approximation."""
    R = 6371000  # Earth radius in meters
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1) * math.cos(math.radians(lat1))  # Adjust for latitude
    x = R * dlon
    y = R * dlat
    return x, y

def interpolate_points(start, end, step):
    """Generate points along the line segment between start and end."""
    x1, y1 = start
    x2, y2 = end
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    num_points = int(distance // step)

    points = []
    for i in range(num_points + 1):
        t = i / num_points
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        points.append((x, y))
    return points