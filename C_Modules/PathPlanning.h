#include <stdio.h>
#include <math.h>

// width of distance between points
double width = 2; 
//maxium width we can see
double max_y_dist = 10;

double *GeneratePath(float *cords){
    bool double_side_flag = false;
    //if cords are too wide, check both sides

    int num_stops = floor(cords[0] / width);
    if(cords[1] > max_y_dist){
        num_stops = 2*num_stops;
        double_side_flag=true;
        }

    double path[num_stops+1][2];
    
    //path starts at relative x,y coordinates
    path[0][0] = 0;
    path[0][1] = 0;
    

    if(!double_side_flag){
        for(int i=1;i<num_stops;i++){
            path[i][1] = 0;
            path[i][0] = path[i-1][0] + width;
            }
        path[num_stops][0]= cords[0]
        path[num_stops][1]= cords[1]
        
    }

    else 
    {      
        
    } 
};