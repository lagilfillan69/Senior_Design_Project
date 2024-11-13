from ultralytics import YOLO
import time,os
YOLOHome = os.getcwd().replace('\\','/')+'/'


folder_path = "demo-stereo_1920x1188.yolov8"
#"demo-25p_1500x842.yolov8"
#"demo-stereo_1920x1188.yolov8"




#make model
model = YOLO('yolov8s.pt')

#train
start_time = time.time()
model.train(data=YOLOHome+folder_path+'/data.yaml', epochs=1, rect=True)
end_time = time.time()
print(f'model2 Train Time:\t{end_time-start_time}')


#saving
model.save(YOLOHome+folder_path[:-7]+'__BestModel.pt')
model.export(format='onnx', imgsz=None, name=YOLOHome+folder_path[:-7]+'__BestModel.pt')
