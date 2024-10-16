# Written by Jonah Earl Belback

# Stable container for Serial Communication from Jettson to ESP32

#going to be using these libraries, but until can start working with ESP32 not sure exactly how
import serial, pyfirmata2

try:
    from helper_functions import *
    from SD_constants import ESP32_PORT #needs to be manually set
except:
    from Py_Modules.helper_functions import *
    from Py_Modules.SD_constants import ESP32_PORT #needs to be manually set

#WERE DOING ARDUINO NOW PYFRIMATA



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



prGreen("Serial_ESP32: Class Definition Success")
#===============================================================================



if __name__ == "__main__":
    pass

