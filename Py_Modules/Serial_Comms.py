# Written by Jonah Earl Belback

# Stable container for Serial Communication from Jettson to ESP32

from SD_constants import ESP32_PORT

import os,sys
dir_path = os.path.abspath("")
print(f"DIRECTORY:\t\t<{dir_path}>")
sys.path.append(dir_path)
from fun_colors import *






class Serial_ESP32:
    def __init__(self,Port=ESP32_PORT):
        pass