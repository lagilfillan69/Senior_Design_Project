# Written by Lauren Gilfillan

# Convert GPS coordinates to Rectangle Path Plan for Robot


try:
    from helper_functions import GPStoXY
except:
    from Py_Modules.helper_functions import GPStoXY

import math
import numpy as np

#Max seeing distance of the bot in height and width in meters
RANGE_WIDTH = 10.0
RANGE_HEIGHT= 10.0 
START = [0,0]
#based on the input coordinates we make assumptions on how we are gonna layout our path. 
#the shorter side will always be considered the height, while the longer side will be our width
                                    # (Boundary,Boundary)
# |--------------------------------------|
# |                                      |
# |    <-- height         |              |
# |                 width v              |
# |--------------------------------------|
# (0,0)
def PathPlan(cords):
    boundary = GPStoXY(cords)
    print("X Y Coordinates",boundary)

    if(abs(boundary[0]) > abs(boundary[1])):
        width = boundary[0]
        height = boundary[1]
    else :
        width = boundary[0]
        height = boundary[1]

    # width = 105
    # height = 55

    
    max_width_points = math.ceil(abs(width)/RANGE_WIDTH)
    max_height_points = math.ceil(abs(height)/RANGE_HEIGHT)
    num_points = 2*max_width_points+2*max_height_points + 1
    path = np.zeros((num_points,2))

    #establish four edge points
    path[max_width_points,0] = width
    path[max_height_points + max_width_points,0] = width
    path[max_height_points + max_width_points,1] = height
    path[max_height_points + max_width_points + max_width_points,1] = height


    #populating points 
    for i in range(1,num_points) :
        if(i <= max_width_points):
            path[i,1] = path[i-1,1]
            if(width < 0):
                if(path[i-1,0] - RANGE_WIDTH < width):
                    path[i,0] = width
                else:
                    path[i,0] = path[i-1,0] - RANGE_WIDTH
            elif(width > 0):
                if(path[i-1,0] + RANGE_WIDTH > width):
                    path[i,0] = width
                else:
                    path[i,0] = path[i-1,0] +RANGE_WIDTH
        elif(max_width_points < i <= max_width_points + max_height_points ):
            path[i,0] = path[i-1,0]
            if(height > 0):
                if (path[i-1,1] + RANGE_HEIGHT) > height:
                    path[i,1] = height
                else:
                    path[i,1] = path[i-1,1] + RANGE_HEIGHT
            else : 
                if (path[i-1,1] - RANGE_HEIGHT) < height:
                    path[i,1] = height
                else:
                    path[i,1] = path[i-1,1] - RANGE_HEIGHT
        elif(max_width_points + max_height_points < i <=  2*max_width_points + max_height_points):
            path[i,1] = path[i-1,1]
            if(width > 0):
                if (path[i-1,0] - RANGE_WIDTH < 0):
                    path[i,0] = 0
                else:
                    path[i,0] = path[i-1,0] - RANGE_WIDTH
            else:
                if (path[i-1,0] + RANGE_WIDTH > 0):
                    path[i,0] = 0
                else:
                    path[i,0] = path[i-1,0] + RANGE_WIDTH
            
        elif(i >= 2*max_width_points + max_height_points):
            path[i,0] = path[i-1,0]
            if(height > 0):
                if path[i-1,1] - RANGE_HEIGHT < 0:
                    path[i,1] = 0
                else:
                    path[i,1] = path[i-1,1] - RANGE_HEIGHT
            else : 
                if path[i-1,1] + RANGE_HEIGHT > 0:
                    path[i,1] = 0
                else:
                    path[i,1] = path[i-1,1] + RANGE_HEIGHT
            
    print("Path : ", path)
    return path


if __name__ == "__main__":
    
    #definition of main
    def main():
        print("Testing Path Planning")

        # lat = input("Please enter GPS Lat Cord 1:")

        # lat_dig = float(lat)

        # long = input("Please enter GPS Long Cord 1:")
        # long_dig = float(long)

        # lat_2 = input("Please enter GPS Lat Cord 2:")

        # lat_dig2 = float(lat_2)

        # long2 = input("Please enter GPS Long Cord 2:")
        # long_dig2 = float(long2)



        # print("Calculating Path......\n")

        # PP.PathPlan([lat_dig,long_dig,lat_dig2,long_dig2])

        PathPlan([40.35729,-79.93397,40.35604,-79.93218])

        return 0
    
    main()
    exit(0)