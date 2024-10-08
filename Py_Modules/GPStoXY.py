import math

def GPStoXY(cords):
    # Convert degrees to radians
    lat1 = math.radians(cords[0])
    lon1 = math.radians(cords[1])
    lat2 = math.radians(cords[2])
    lon2 = math.radians(cords[3])

    # Earth's radius in meters
    R = 6371000  

    # Calculate relative x and y coordinates
    x = R * (lon2 - lon1) * math.cos((lat1 + lat2) / 2)
    y = R * (lat2 - lat1)
    print(" X : ", x, " Y : ", y)

    return (x, y)