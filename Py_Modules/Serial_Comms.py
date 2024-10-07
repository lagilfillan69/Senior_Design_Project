# Written by Jonah Earl Belback

# Stable container for Serial Communication from Jettson to ESP32

from SD_constants import ESP32_PORT

import os,sys
dir_path = os.path.abspath("")
print(f"DIRECTORY:\t\t<{dir_path}>")
sys.path.append(dir_path)
from fun_colors import *


#going to be using these libraries, but until can start working with ESP32 not sure exactly how
import serial, Pyfirmata2




class Serial_ESP32:
    def __init__(self,Port=ESP32_PORT):
        pass
    
    def read_message(self):
        return ""
    
    def send_message(self,mes):
        pass
