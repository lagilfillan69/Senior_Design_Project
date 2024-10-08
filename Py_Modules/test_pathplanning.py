import Path_Planning as PP
import math

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

    PP.PathPlan([40.35729,-79.93397,40.35604,-79.93218])

    return 0


if __name__ == "__main__":
    main()
    exit(0)