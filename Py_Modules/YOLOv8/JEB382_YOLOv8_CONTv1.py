# Written by Jonah Earl Belback

# YOLOv8n stable module container


#-------
import ultralytics
from ultralytics import YOLO
from ultralytics import settings
#------------------------
import os,sys,time,shutil,cv2
import matplotlib.pyplot as plt
import numpy as np

dir_path = os.path.abspath("")
print(f"DIRECTORY:\t\t<{dir_path}>")
sys.path.append(dir_path)

global YOLO_home
YOLO_home = (os.getcwd()+'/YOLOv8/').replace('\\','/')
print(f"HOME:\t\t<{YOLO_home}>")

from fun_colors import *
#------------------------


#===============================================================================
'''
vers: type of YOLOv8 model
    - n(nano)
    - s(mall), larger
    - else raises error
    
modelpath: either:
    - directpath to a YOLOv8 model
    or
    - its training folder: find latest 'best.pt' file
    
verbose: passed YOLOv8 attribute, deals with YOLO printouts

'''

class YOLO_model_v1:
    def __init__(self, vers='n', model_path=None,verbose=False,model_type='classify'):
        #check library
        ultralytics.checks()
        self.verbose=verbose
        
        #---------------------------------------
        # NOTE: Model Creation
        
        #make new model
        if model_path == None:
            prGreen("Creating new model")
            #load version
            if vers.lower() == 'n': self.model = YOLO(YOLO_home+"loadable_models/defaults/yolov8n.pt",verbose=self.verbose)#,task='classify')
            elif vers.lower() == 's': self.model = YOLO(YOLO_home+"loadable_models/defaults/yolov8s.pt",verbose=self.verbose)#,task='classify')
            else: raise ValueError(f"YOLOv8 version not found: <_{vers}_>")
            self.pretrain=False
            self.full_model = True
            
            prGreen("SUCCESS: MODEL CREATED")
            
        #load latest model from a directory
        else:
            self.load_model(model_path)
            self.pretrain=True
        
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
                prLightPurple('From Directory:\t'+latest_model)
                self.model = YOLO(latest_model,verbose=self.verbose)#,task='classify')
                self.full_model = True
            
            except Exception as e:
                prALERT(str(e))
                os._exit()
        
        #load model but cant train
        elif model_path[-3:] !='.onnx':
            prALERT("Please double check your   < hyperparameters >   are aligned with saved model")
            prLightPurple('From File:\t'+model_path)
            self.model = YOLO(model_path,verbose=self.verbose)#,task='classify')
            self.full_model = False
                
        #load model from file   
        else:
            prALERT("Please double check your   < hyperparameters >   are aligned with saved model")
            prLightPurple('From File:\t'+model_path)
            self.model = YOLO(model_path,verbose=self.verbose)#,task='classify')
            self.full_model = True
        
        prGreen("SUCCESS: MODEL LOADED")
    
    
    # ========================================
    def run_model(self,data_path):
        results = self.model(data_path)  # predict on an image file
        arr = [];temp=[]        
        for obj in results:            
            if obj.boxes.xyxy.shape[0] == 0: continue #catch empty results
            xyxy = list(obj.boxes.xyxy.numpy()[0])
            arr.append( [   obj.names[ int(obj.boxes.cls.numpy()[0]) ],  [xyxy[:2],xyxy[2:]]   ] )
        
        #list of list of individual object properties [ classification, [Top right BB corod, Bottom Left] ]
        return arr
    
    
    '''
    opt: optimizer
        - None: let YOlO decide which on to use
        - SGD:
        - Adam:
        - AdamW:
        - NAdam:
        - RAdam:
        - RMSProp:
    
    pretrained: if false, resets weights to random values
    
    imgsize: YOLOv8 uses a square image (if rect false), resizes. set this to you highest dimension in the image
    
    rect: if image is rectangular
    '''
    # ========================================
    def train_model(self,data_path,iter=1,opt=None,imgsize=[512,384],rect=True):
        
        if not self.full_model: raise TypeError(f"Loaded Model is not full (.onnx not .pt): Cannot *Train*, can only *Run*")
        
        # check optimizer is valid
        if opt not in [None,'SGD','Adam','AdamW','NAdam','RAdam','RMSProp']: raise ValueError(f"Optimizer not found: {opt}")
        
        # train the model
        if opt==None:
            train_obj = self.model.train(
                data=data_path,
                epochs=iter,
                # optimizer=opt,
                pretrained=self.pretrain,
                imgsz=imgsize,
                rect=rect
                )
        else:
            train_obj = self.model.train(
                data=data_path,
                epochs=iter,
                optimizer=opt,
                pretrained=self.pretrain,
                imgsz=imgsize,
                rect=rect
                )
        
        self.pretrain=True
        return train_obj.save_dir


#==========================================================





#==========================================================
#Test Cases


if __name__ == "__main__":
    import time
    
    
    
    # init model outside container -----------------------------------------------
    print( Back.RED+"\n\ninit model outside container -----------------------------------------------"+Style.RESET_ALL )
    test_model = YOLO(YOLO_home+"loadable_models/defaults/yolov8n.pt")
    
    
    
    
    
    # init model (n) -----------------------------------------------
    print( Back.RED+"\n\ninit model (n) -----------------------------------------------"+Style.RESET_ALL )
    test_model = YOLO_model_v1()
    print(Back.CYAN+f'model1 pretrain:\t{test_model.pretrain}'+Style.RESET_ALL)
    #training
    start_time = time.time()
    save_dir = test_model.train_model(YOLO_home+'datasets/example_dataset/data.yaml')
    end_time = time.time()
    print(Back.CYAN+f'model1 pretrain:\t{test_model.pretrain}'+Style.RESET_ALL)
    print(Back.CYAN+f'model1 Train Time:\t{end_time-start_time}'+Style.RESET_ALL)
    print(Back.CYAN+f'model1 Train output:\t{save_dir}'+Style.RESET_ALL)
    #running
    start_time = time.time()
    result = test_model.run_model(YOLO_home+'datasets/TEST_example.jpg')
    end_time = time.time()
    print(Back.CYAN+f'model1 Runtime:\t{end_time-start_time}'+Style.RESET_ALL)
    print(Back.CYAN+f'model1 Run output:\t{result}'+Style.RESET_ALL)
    
    
    
    
    
    # init model (s) -----------------------------------------------
    print( Back.RED+"\n\ninit model (s) -----------------------------------------------"+Style.RESET_ALL )
    test_model = YOLO_model_v1(vers='s')
    print(Back.CYAN+f'model2 pretrain:\t{test_model.pretrain}'+Style.RESET_ALL)
    #training
    start_time = time.time()
    save_dir = test_model.train_model(YOLO_home+'datasets/example_dataset/data.yaml')
    end_time = time.time()
    print(Back.CYAN+f'model2 pretrain:\t{test_model.pretrain}'+Style.RESET_ALL)
    print(Back.CYAN+f'model2 Train Time:\t{end_time-start_time}'+Style.RESET_ALL)
    print(Back.CYAN+f'model2 Train output:\t{save_dir}'+Style.RESET_ALL)
    #running
    start_time = time.time()
    result = test_model.run_model(YOLO_home+'datasets/TEST_example.jpg')
    end_time = time.time()
    print(Back.CYAN+f'model2 Runtime:\t{end_time-start_time}'+Style.RESET_ALL)
    print(Back.CYAN+f'model2 Run output:\t{result}'+Style.RESET_ALL)
    
    
    
    
    
    # loading model (.pt) -----------------------------------------------
    print( Back.RED+"\n\nloading model (.pt) -----------------------------------------------"+Style.RESET_ALL )
    test_model = YOLO_model_v1(model_path=YOLO_home+'loadable_models/example_model.pt')
    print(Back.CYAN+f'model3 pretrain:\t{test_model.pretrain}'+Style.RESET_ALL)
    #training
    start_time = time.time()
    save_dir = test_model.train_model(YOLO_home+'datasets/example_dataset/data.yaml')
    end_time = time.time()
    print(Back.CYAN+f'model3 pretrain:\t{test_model.pretrain}'+Style.RESET_ALL)
    print(Back.CYAN+f'model3 Train Time:\t{end_time-start_time}'+Style.RESET_ALL)
    print(Back.CYAN+f'model3 Train output:\t{save_dir}'+Style.RESET_ALL)
    #running
    start_time = time.time()
    result = test_model.run_model(YOLO_home+'datasets/TEST_example.jpg')
    end_time = time.time()
    print(Back.CYAN+f'model3 Runtime:\t{end_time-start_time}'+Style.RESET_ALL)
    print(Back.CYAN+f'model3 Run output:\t{result}'+Style.RESET_ALL)
    
    
    
    
    
    # loading model (folder) -----------------------------------------------
    print( "\n\nloading model (folder) -----------------------------------------------"+Style.RESET_ALL )
    test_model = YOLO_model_v1(model_path=YOLO_home+'loadable_models')