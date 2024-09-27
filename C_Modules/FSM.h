#include <stdio.h>
#include <math.h>

int current_state=0;
int path_index=-1; 
double[][] path_plan; 

void Stop_State(void);
    //Call motor stop
void Start_State(void){
    //get GPS Coordinates
    //
};


void Plan_Path_State(void);

void Object_Detected_State(void);

void Travel_To_State(void);

void Return_To_Path(void);

void Check_Object(void)