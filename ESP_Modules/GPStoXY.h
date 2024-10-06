#include <stdio.h>
#include <math.h>

double toRadians(double degree) {
    return degree * (3.14159265358979323846 / 180.0);
}

double *GPStoXY(double *cord) {
    // Convert lat/lon to radians
    double lat1_rad = toRadians(cord[0]);
    double lon1_rad = toRadians(cord[1]);
    double lat2_rad = toRadians(cord[3]);
    double lon2_rad = toRadians(cord[4]);

    // Earth's radius in meters
    const double R = 6371000;

    // Calculate x, y offsets in meters 
    double x = R * (lon2_rad - lon1_rad) * cos((lat1_rad + lat2_rad) / 2);
    double y = R * (lat2_rad - lat1_rad);
    double cart_cord[2] = {x,y};
    return cart_cord;
}

