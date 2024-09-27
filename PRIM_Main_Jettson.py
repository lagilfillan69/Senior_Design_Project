# Main on Jettson
# Primary Main: Responsible for decision making process, tells ESP32 what to do through serial
#   - see Serial_Comms

from Py_Modules.YOLOv8.JEB382_YOLOv8_CONTv1 import YOLO_model_v1
from Py_Modules.Depth_Camera import *
from Py_Modules.Serial_Comms import *