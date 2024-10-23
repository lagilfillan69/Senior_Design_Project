# Written by Lauren Gilfillan

# Convert GPS coordinates to Rectangle Path Plan for Robot


try:
    from helper_functions import GPStoXY,prGreen
    from SD_constants import PP_RANGE_WIDTH,PP_RANGE_HEIGHT,PP_START#needs to be manually set
except:
    from Py_Modules.helper_functions import GPStoXY,prGreen
    from Py_Modules.SD_constants import PP_RANGE_WIDTH,PP_RANGE_HEIGHT,PP_START#needs to be manually set
import math
import numpy as np

#based on the input coordinates we make assumptions on how we are gonna layout our path. 
#the shorter side will always be considered the height, while the longer side will be our width
                                    # (Boundary,Boundary)
# |--------------------------------------|
# |                                      |
# |    <-- height         |              |
# |                 width v              |
# |--------------------------------------|
# (0,0)
def PathPlan(cords,verbose=False):
    boundary = GPStoXY(cords,verbose)
    if verbose: print("X Y Coordinates",boundary)

    if(abs(boundary[0]) > abs(boundary[1])):
        width = boundary[0]
        height = boundary[1]
    else :
        width = boundary[0]
        height = boundary[1]

    # width = 105
    # height = 55

    
    max_width_points = math.ceil(abs(width)/PP_RANGE_WIDTH)
    max_height_points = math.ceil(abs(height)/PP_RANGE_WIDTH)
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
                if(path[i-1,0] - PP_RANGE_WIDTH < width):
                    path[i,0] = width
                else:
                    path[i,0] = path[i-1,0] - PP_RANGE_WIDTH
            elif(width > 0):
                if(path[i-1,0] + PP_RANGE_WIDTH > width):
                    path[i,0] = width
                else:
                    path[i,0] = path[i-1,0] +PP_RANGE_WIDTH
        elif(max_width_points < i <= max_width_points + max_height_points ):
            path[i,0] = path[i-1,0]
            if(height > 0):
                if (path[i-1,1] + PP_RANGE_HEIGHT) > height:
                    path[i,1] = height
                else:
                    path[i,1] = path[i-1,1] + PP_RANGE_HEIGHT
            else : 
                if (path[i-1,1] - PP_RANGE_HEIGHT) < height:
                    path[i,1] = height
                else:
                    path[i,1] = path[i-1,1] - PP_RANGE_HEIGHT
        elif(max_width_points + max_height_points < i <=  2*max_width_points + max_height_points):
            path[i,1] = path[i-1,1]
            if(width > 0):
                if (path[i-1,0] - PP_RANGE_WIDTH < 0):
                    path[i,0] = 0
                else:
                    path[i,0] = path[i-1,0] - PP_RANGE_WIDTH
            else:
                if (path[i-1,0] + PP_RANGE_WIDTH > 0):
                    path[i,0] = 0
                else:
                    path[i,0] = path[i-1,0] + PP_RANGE_WIDTH
            
        elif(i >= 2*max_width_points + max_height_points):
            path[i,0] = path[i-1,0]
            if(height > 0):
                if path[i-1,1] - PP_RANGE_HEIGHT < 0:
                    path[i,1] = 0
                else:
                    path[i,1] = path[i-1,1] - PP_RANGE_HEIGHT
            else : 
                if path[i-1,1] + PP_RANGE_HEIGHT > 0:
                    path[i,1] = 0
                else:
                    path[i,1] = path[i-1,1] + PP_RANGE_HEIGHT
            
    if verbose: print("Path :\n", path)
    return path



prGreen("Path Planing: Func Definition Success")
#===============================================================================

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

        PathPlan([40.35729,-79.93397,40.35604,-79.93218],verbose=True)

        return 0
    
    main()
    exit(0)