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


#mine
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

def csv_size(filepath):
    try:
        df_iter = pandas.read_csv(filepath)
        return df_iter.shape[0]
    except Exception as e:
        prALERT('csv_size\n'+e)
        sze=0
        df_iter = pandas.read_csv(filepath, iterator=True, chunksize=1)
        while True:
            try:
                df = next(df_iter)
                sze+=1
            except StopIteration:
                break
        return sze

       
#===================
import os,cv2
#find latest YOLOv8 file from a folder or then latest best.pt in subfolders
def YOLOv8_find_latest(folder_path):
    folder_list = os.listdir(folder_path)
    file_list = [ i for i in folder_list if i[-3:] == '.pt']
    folder_list.reverse()
    file_list.reverse()
    # print( folder_list )
    # print( file_list )

    if file_list: return f'{folder_path}/{file_list[0]}'

    for folder in folder_list:
        if os.path.isfile(f'{folder_path}/{folder}/weights/best.pt'): return f'{folder_path}/{folder}/weights/best.pt'
    return None


def reduce_found_obj(file_path, coords, output_path, Expan_rate=0.7, Compress_rate=10):
    #read
    img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    
    #crop
    img = img[ int(coords[0][1]*Expan_rate):int( img.shape[0]-(img.shape[0]-coords[1][1])*Expan_rate ),  int(coords[0][0]*Expan_rate):int( img.shape[1]-(img.shape[1]-coords[1][0])*Expan_rate )  ]
    
    #compress
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), Compress_rate]
    _, encimg = cv2.imencode('.jpg', img, encode_param)
    decoded_img = cv2.imdecode(encimg, cv2.IMREAD_GRAYSCALE)
    
    cv2.imwrite(output_path, decoded_img )