from Path_Planning import PathPlan

# State Legend
# 0 - Stop
# 1 - Start
# 2 - Pause
# 3 - Drive to next path coorindates
# 4 - Detect Objects
# 5 - Object Located (waiting)
# 6 - Drive to Object (relative)
# 7 - Drive to Object (precise)
# 8 - Vaccum Object
# 9 - Return to Path Cord

Preivous_State = 0
State = 0
Current_Cordinate = []
Path_Index = -1
Current_Location = [0,0]
Trash_Detected_Locations = []
Trash_Collected_Locations = []
Trash_Index = -1
Relative_Direction = "Null"
Retrieve_Object = False




############COMMUNICATION FROM Detection#################
# "Object Detected relative" 
# "No Object Detected "
# "Object Detected precise"
#  
# 

def main():
    while(1):
        #get current location from motor driver
        Current_Location = [0,0] #Input from Motor Driver
        
        #notification from Detector 
        Notification = ""
        if(Notification == "Object Detected relative : Direction "):
            if (State ==  4) : #Safe Guarding Against Random Communication
                State = 5
            Relative_Direction = "Direction"
               
        elif(Notification == "Object Detected precise : [x,y]") :
                State = 5
                Trash_Index += 1; 
                Trash_Detected_Locations[Trash_Index] = [0,0]
        
        elif(Notification == "No Object Detected"):
            State == 3

############COMMUNICATION FROM UI#################
# 0 = Stop
# 1 = Start, GPS Coordinates to Come 
# 2 = Pause 
# 3 = Pick Up Detected Object 
# 4 = Do not pick up Detected Object

        
        #read most recent UI message
        #UI always trumps everything else in terms of control
        UI_Message =  0 #int(Input from Serial)

        if UI_Message  : #new message from UI? 
            if(UI_Message == 0)) : 
                State = 0
                
            elif(UI_Message == 1) : 
                State = 1

            elif(UI_Message == 2)) : 
                State = 2
                
            elif(UI_Message == 3) : 
                State = 6

            elif(UI_Message == 4) : 
                State = 3


        # STOP
        if(State == 0):
            Path_Index = -1
            print("To Motor Controller : Motor Stop")
            print("To Detector : Stop")
            Previous_State = 0
        #START 
        elif(State == 1):
            print("From UI : Start")
            #generate Path 
            while("wait for GPS coordinates"):
                  print("Waiting for GPS")
                  #dead loop untill given coordinates through serial
            cords = [0,0] # serial input
            Path = PathPlan(cords)
            Path_Index = 0 
            Previous_State = 1
        
        #PAUSE
        elif(State == 2):
            print("To Motor Driver : Stop Motors")
            print("To Detector : Stop Detecting")
            print("Waiting for UI to tell me to Start or Stop")
            Previous_State = 2

        #Go to Next Path Index
        elif(State == 3):    
            #edge case, try to travel with no path
            if(Path_Index == -1):
                State = 0
            else :
                if not(Preivous_State==3):
                    Path_Index += 1
                print("To Motor Driver : Move to [X,Y]")
                if (Current_Location == Path[Path_Index]):
                    State = 4
                else : 
                    State = 3
            Preivous_State = 3

        #Detect Objects
        elif(State == 4):
            print("Send to Detector : Start looking for Objects")
            print("Send to Motor Driver : Spin in a Circle")
            #will stay in this mode until notified that an object is found or not found
            State = 4
            Previous_State = 4

        #Object Located (Notify Officals)
        elif(State == 5):
            print("Send to UI : Object Detected ")
            # Will stay in this state untill a response"
            Previous_State = 5

        #Drive to Object (relative)
        elif(State == 6):
            print("To Motor Driver : Left, Right, Center")
            #Will stay in this state until there is a precise location found or object is lost
            State = 6
            Previous_State = 6
        
        #Drive to Object (precise)
        elif(State == 7):
            print("To Motor Driver : Drive to [X,Y] location")

            # will stay in this state until we are at set locations
            if(Current_Location == Trash_Detected_Locations[Trash_Index]):
                State=8
            else : 
                State =7
            Previous_State = 7

        #Vaccum Object
        elif(State == 8):
            print("Turn on Vaccum, wait 30 seconds, turn off vaccum")
            State = 9
            Previous_State = 8
        
        # 9 - Return to Path Cord
        elif(State == 9):
            #will stay in this stay in this state until cordinates are reached
            if(Current_Location == Path[Path_Index]):
                State = 4
            else :
                State = 9
            Preivous_State = 9
