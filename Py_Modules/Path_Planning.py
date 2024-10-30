# Written by Lauren Gilfillan

# Convert GPS coordinates to Rectangle Path Plan for Robot


try:
    from helper_functions import GPStoXY
    from helper_functions import haversine_distance
    from helper_functions import interpolate_points
except:
    from Py_Modules.helper_functions import haversine_distance
    from Py_Modules.helper_functions import gps_to_xy
    from Py_Modules.helper_functions import interpolate_points

import math
import numpy as np

#Max seeing distance of the bot in height and width in meters
RANGE_WIDTH = 5.0
RANGE_HEIGHT= 5.0 

#based on the input coordinates we make assumptions on how we are gonna layout our path. 
#the shorter side will always be considered the height, while the longer side will be our width
                                    # (Boundary,Boundary)
# |--------------------------------------|
# |                                      |
# |    <-- height         |              |
# |                 width v              |
# |--------------------------------------|
# (0,0)
def generate_path(p1, p2, p3, step=5):
    """Generate a path around the rectangle formed by the three GPS points."""
    # Convert GPS to Cartesian coordinates
    origin = (0, 0)
    x2, y2 = gps_to_xy(*p1, *p2)  # From p1 to p2
    x3, y3 = gps_to_xy(*p1, *p3)  # From p1 to p3

    # Define the four corners of the rectangle
    corners = [origin, (x2, y2), (x2 + x3, y2 + y3), (x3, y3)]

    # Generate path along the rectangle edges
    path = []
    for i in range(4):
        start = corners[i]
        end = corners[(i + 1) % 4]
        path += interpolate_points(start, end, step)

    # Return path back to origin
    path.append(origin)
    return path
