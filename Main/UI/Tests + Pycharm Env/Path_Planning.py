# Written by Lauren Gilfillan
# Convert GPS coordinates to Rectangle Path Plan for Robot


# try:
from helper_functions import gps_to_xy
from helper_functions import haversine_distance
from helper_functions import interpolate_points
# except:
#     from Py_Modules.helper_functions import haversine_distance
#     from Py_Modules.helper_functions import gps_to_xy
#     from Py_Modules.helper_functions import interpolate_points

import math
import numpy as np

#Max seeing distance of the bot in height and width in meters
RANGE_WIDTH = 5.0
RANGE_HEIGHT= 5.0 

def generate_corners(p1, p2, p3, step=5):
       # Convert GPS to Cartesian coordinates relative to p1
    origin = (0, 0)
    x2, y2 = gps_to_xy(*p1, *p2)  # Cartesian from p1 to p2
    x3, y3 = gps_to_xy(*p1, *p3)  # Cartesian from p1 to p3

    x4, y4 = x2 + x3, y2 + y3

   
    corners = [origin, (x2, y2), (x3, y3), (x4, y4)]

    unique_corners = list(dict.fromkeys(corners))
    return unique_corners


def generate_path(unique_corners,origin,step=5):
    path = []
    for i in range(len(unique_corners)):
        start = unique_corners[i]
        end = unique_corners[(i + 1) % len(unique_corners)]
        path += interpolate_points(start, end, step)

    path.append(origin)

    return path
