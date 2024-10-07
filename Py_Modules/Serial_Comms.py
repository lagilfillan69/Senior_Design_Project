# Written by Jonah Earl Belback

# Stable container for Serial Communication from Jettson to ESP32

from SD_constants import ESP32_PORT

import os,sys
dir_path = os.path.abspath("")
if __name__ == "__main__": print(f"DIRECTORY:\t\t<{dir_path}>")
sys.path.append(dir_path)
from fun_colors import *


#going to be using these libraries, but until can start working with ESP32 not sure exactly how
import serial, Pyfirmata2




class Serial_ESP32:
    def __init__(self,Port=ESP32_PORT):
        pass
    
    def read_message(self):
        pass
    
    def send_message(self,mes):
        pass
    
    #==============================
    
    def Motor(self,arr):
        self.send_message(f"MOTOR\t{arr}")  #The exact framing of this message is still TBD
        pass

    def Bluetooth(self,mes):
        self.send_message(f"BLUETOOTH\t{mes}")  #The exact framing of this message is still TBD
        pass

