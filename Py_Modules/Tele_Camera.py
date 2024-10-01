# Written by Jonah Earl Belback

# Stable container for Telescopic Camera

import cv2,device



class TeleCAM():
    def __init__(self):
        pass


#==========================================================





#==========================================================
#Test Cases


if __name__ == "__main__":
    
    device_list = device.getDeviceList()
    for index, camera in enumerate(device_list):
        print(f"{index}: {camera[0]} {camera[1]}")