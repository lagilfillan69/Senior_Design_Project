# YOLOv8n stable module container






#-------
import ultralytics
from ultralytics import YOLO
from ultralytics import settings
#------------------------
import os,sys,time,shutil
import numpy as np
dir_path = os.path.abspath("")
print(f"DIRECTORY:\t\t<{dir_path}>")
sys.path.append(dir_path)
from fun_colors import *
#------------------------
PTV2_HYPER_DEF=[24,128*2,0.2,10,1000,30000,100,1e-3,200,64,4,4,0.0]


#===============================================================================
'''
vers: type of YOLOv8 model
    - n(nano)
    - s(mall), larger
    - else raises error
modelpath: either
    - directpath to a YOLOv8 model
    or
    - its training folder: find latest 'best.pt' file

'''

class YOLO_model_v1:
    def __init__(self, vers='n', hyperparameters=PTV2_HYPER_DEF, model_path=None,name=None):
        #check library
        ultralytics.checks()
        
        #---------------------------------------
        # NOTE: Model Creation
        
        #make new model
        if model_path == None:
            prGreen("Creating new model")
            #load version
            if vers.lower() == 'n': self.model = YOLO("yolov8n.pt")
            elif vers.lower() == 's': self.model = YOLO("yolov8s.pt")
            else: raise ValueError(f"YOLOv8 version not found: <_{vers}_>")
            
            prGreen("SUCCESS: MODEL CREATED")
            
        #load latest model from a directory
        else: self.load_model(model_path)
        
        #---------------------------------------    
        #disable bad API
        os.environ['WANDB_MODE'] = 'disabled'
        settings.update({"wandb": False})
        
        
        #---------------------------------------
        print(Back.GREEN+"SUCCESS: MODEL INIT PASS"+Style.RESET_ALL)
            
    
    
    # ========================================
    def save_model(self,dir_path):
        path = self.model.export(format='onnx',verbose=False)
    
        sp = dir_path.split('.')
        if len(sp)>1:
            if sp[-1] != 'onnx':
                #.(not onnx) file_path
                export = shutil.copyfile(path, '.'.join(sp[:-1])+'.onnx')
            else:
                #.onnx file_path (correct)
                export = shutil.copyfile(path, dir_path)
        else:
            #folder file_path
            export = shutil.copyfile(path, f'{dir_path}/Unnamed_save.onnx')
        #delete old file
        os.remove(path)
        
        prGreen("SUCCESS: MODEL SAVED")
        return export
    
    
    # ========================================
    def load_model(self,model_path):
        if model_path[-3:] !='.pt':
            prGreen("Loading latest")
            latest_model = YOLOv8_find_latest(model_path)
            
            if latest_model == None: raise LookupError(f"Cannot find .pt in folder or best.pt in subfolders: {model_path}")
            
            try:
                #load model from file
                prALERT("Please double check your   < hyperparameters >   are aligned with saved model")
                prLightPurple(latest_model)
                self.model = YOLO(dir_path)
            
            except Exception as e:
                prALERT(str(e))
                os._exit()
                
        #load model from file   
        else:
            prALERT("Please double check your   < hyperparameters >   are aligned with saved model")
            prLightPurple(model_path)
            self.model = YOLO(dir_path)
        
        prGreen("SUCCESS: MODEL LOADED")
    
    
    # ========================================
    def run_model(self,data=None,length=256,verbose=False):
        pass


#==========================================================

#find latest YOLOv8 file from a folder or then latest best.pt in subfolders
def YOLOv8_find_latest(folder_path):
    folder_list = os.listdir('C:/Users/jump3/Desktop/curr school/Senior_Design-ML/runs/detect')
    file_list = [ i for i in folder_list if i[-3:] == '.pt']
    folder_list.reverse()
    file_list.reverse()
    # print( folder_list )
    # print( file_list )

    if file_list: return f'{folder_path}/{file_list[0]}'

    for folder in folder_list:
        if os.path.isfile(f'{folder_path}/{folder}/weights/best.pt'): return f'{folder_path}/{folder}/weights/best.pt'
    return None







#==========================================================

if __name__ == "__main__":
    pass