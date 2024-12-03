# Written by Lauren Gilfillan
# Convert GPS coordinates to Rectangle Path Plan for Robot

import math,platform
import numpy as np
import matplotlib.pyplot as plt

try: from helper_functions import haversine_distance, gps_to_xy, interpolate_points, sort_corners, is_valid_polygon
except Exception as e:
    from Py_Modules.helper_functions import haversine_distance, gps_to_xy, interpolate_points
    #raise RuntimeError("Import Error:\n") from e


#Max seeing distance of the bot in height and width in meters
RANGE_WIDTH = 5.0
RANGE_HEIGHT= 5.0 

def generate_corners(p1, p2, p3, p4, step=5):
    origin = (0, 0)
    x2, y2 = gps_to_xy(*p1, *p2)  # Cartesian from p1 to p2
    x3, y3 = gps_to_xy(*p1, *p3)  # Cartesian from p1 to p3
    x4, y4 = gps_to_xy(*p1, *p4)

    corners = [origin, (x2, y2), (x3, y3), (x4, y4)]

    corners = sort_corners(corners)
    return corners

def generate_path(p1, p2, p3, p4, step=5):
    corners = [p1,p2,p3,p4]
    path = []
    for i in range(len(corners)):
        start = corners[i]
        end = corners[(i + 1) % len(corners)]  # Wrap around to connect the last point to the first
        temp = interpolate_points(start, end, step)
        if temp == [-1, -1]:
            print("Unable to Generate Path\n")
            return None
        path += temp
    path.append((0,0))  # Close the path at the origin
    return path

##test to show and plot 3D Points
#Edge Cases -------
# Non-Real Shape
# All the same point
# Non- regantular shape
def main_test():

    # ###### Test 1 AGC Airport
    # P1 = 40.354104, -79.917796
    # P2 = 40.354482, -79.917781
    # P3 = 40.354459, -79.941089
    # P4 = 40.354065, -79.941017
    # corners = generate_corners(P1, P2,P3,P4)
    # test_path = generate_path(corners[0], corners[1], corners[2],corners[3])
    # x, y = zip(*test_path)
    # fig,ax = plt.subplots()
    # ax.plot(x,y, marker='o', linestyle='-', markersize=3)
    # ax.set_aspect('equal', adjustable='box')
    # plt.savefig("test1.png")
    #
    #
    # # ####### Test 2 AGC Airport Alternative
    # P1 = 40.351944, -79.922481
    # P2 = 40.352148, -79.922392
    # P3 = 40.357376, -79.934256
    # P4 = 40.357119, -79.934399
    # corners = generate_corners(P1, P2, P3, P4)
    # test_path = generate_path(corners[0], corners[1], corners[2], corners[3])
    # x, y = zip(*test_path)
    # fig, ax = plt.subplots()
    # ax.plot(x, y, marker='o', linestyle='-', markersize=3)
    # ax.set_aspect('equal', adjustable='box')
    # plt.savefig("test2.png")
    #
    # # ####### Test 2b AGC Airport Alternative
    # P2 = 40.351944, -79.922481
    # P3 = 40.352148, -79.922392
    # P1 = 40.357376, -79.934256
    # P4 = 40.357119, -79.934399
    # corners = generate_corners(P1, P2, P3, P4)
    # test_path = generate_path(corners[0], corners[1], corners[2], corners[3])
    # x, y = zip(*test_path)
    # fig, ax = plt.subplots()
    # ax.plot(x, y, marker='o', linestyle='-', markersize=3)
    # ax.set_aspect('equal', adjustable='box')
    # plt.savefig("test2b.png")
    #
    #
    # # ####### Test 3 Benedum Alternative
    # P1 = 40.443272, -79.958662
    # P2 = 40.443235, -79.958610
    # P3 = 40.443517, -79.958234
    # P4 = 40.443529, -79.958298
    # corners = generate_corners(P1, P2, P3, P4)
    # test_path = generate_path(corners[0], corners[1], corners[2], corners[3])
    # x, y = zip(*test_path)
    # fig, ax = plt.subplots()
    # ax.plot(x, y, marker='o', linestyle='-', markersize=3)
    # ax.set_aspect('equal', adjustable='box')
    # plt.savefig("test3.png")
    #
    # ####### Test 4 All Same Point
    # P1 = 40.443716, -79.958212
    # P2 = 40.443716, -79.958212
    # P3 = 40.443716, -79.958212
    # P4 = 40.443716, -79.958212
    # corners = generate_corners(P1, P2, P3, P4)
    # test_path = generate_path(corners[0], corners[1], corners[2], corners[3])
    #
    # if test_path is not None:
    #     x, y = zip(*test_path)
    #     fig, ax = plt.subplots()
    #     ax.plot(x, y, marker='o', linestyle='-', markersize=3)
    #     plt.savefig("test4.png")
    # else:
    #     print("Pass")
    #
    #
    # ####### Test 5 Triangle Shape
    #
    # ### Returns None - Faults out of progrgam
    # P1 = 40.443852, -79.958015
    # P2 = 40.443765, -79.958010
    # P3 = 40.443849, -79.957887
    # P4 = 40.443849, -79.957887
    # corners = generate_corners(P1, P2, P3, P4)
    # test_path = generate_path(corners[0], corners[1], corners[2], corners[3])
    # if test_path is None:
    #     print("Test 5 Pass")

    ####### Test 6 Polygon
    P1 = 40.353677, -79.932160
    P2 = 40.353694, -79.931302
    P3 = 40.353342, -79.930157
    P4 = 40.353333, -79.932931
    corners = generate_corners(P1, P2, P3, P4)
    test_path = generate_path(corners[0], corners[1], corners[2], corners[3])
    x, y = zip(*test_path)
    fig, ax = plt.subplots()
    ax.plot(x, y, marker='o', linestyle='-', markersize=3)
    ax.set_aspect('equal', adjustable='box')
    plt.savefig("test6.png")

    ####### Test 6 Straight lINE
    P1 = 40.353677, -79.932160
    P2 = 40.353694, -79.932160
    P3 = 40.353342, -79.932160
    P4 = 40.353333, -79.932160
    corners = generate_corners(P1, P2, P3, P4)
    test_path = generate_path(corners[0], corners[1], corners[2], corners[3])
    x, y = zip(*test_path)
    fig, ax = plt.subplots()
    ax.plot(x, y, marker='o', linestyle='-', markersize=3)
    ax.set_aspect('equal', adjustable='box')
    plt.savefig("test7.png")

if __name__ == '__main__':
    main_test()
