#include <SoftwareSerial.h>


/* Chad stuff */
#include "RotaryEncoder.h"
#include <Servo.h>
#include <Vector.h>

const int bumpSensorPin = 18;  // Interrupt pin connected to the bump sensor
const int outputPin = 13;     // Output pin to set high

// Flag to indicate interrupt has been triggered
volatile bool bumpDetected = false;



int dummy = 0;

Servo steeringServo;
Servo ESC;
int escPin = 9;

void RotaryChanged();

volatile int Counter = 0; // Encoder step counter
int GlobalCount = 0;
int LastCount = 0; // To keep track of changes

RotaryEncoder Rotary(&RotaryChanged, 2, 3, 4); // (CLK),  (DT),  (SW)
volatile unsigned int state = Rotary.GetState();

void RotaryChanged() {
    // Update state and count steps
    const unsigned char pinstate = (digitalRead(2) << 1) | digitalRead(3);
    state = ttable[state & 0x07][pinstate];

    if (state & DIR_CW) {
        Counter--;
    } else if (state & DIR_CCW) {
        Counter++;
    }
}


struct TestRun {
  float distance;
  int iterations;
  int speed;
};

TestRun testData[] = {
  {10.0, 300, 1500},
  {5.0, 150, 1200},
  {1.0, 30, 1100}
};

const int testDataSize = sizeof(testData) / sizeof(testData[0]);

float totalDistanceDriven = 0.0;




SoftwareSerial btSerial(11,10); //RX to DIgital 4, TX to Digital 3


String Command;
String Data;
String Prev;
int split;
int Serial_comms;
int Bluetooth_comms;
float CurrPos_X;
float CurrPos_Y;
float Angle;
float Depth;
String incomingString;
String C1 = "";
String C2 = "";
String C3 = "";
String C4 = "";

String PrevCMD = "";
bool found = false;
bool Rflag =  0;

int steps = 0;

float angleRadians = 0;





  //========================================================
  //Using Comms

  /*
    In State 5, where waiting for approval:
    to approve:   Serial.println("OKAY")
    to not:       Serial.println("NKAY")

    When arrived at point
    Serial.print("CPOS\t[");Serial.print(CurrPos_X);Serial.print(", ");Serial.print(CurrPos_Y);Serial.println("]");
  */

// '''
// Types of __Python__ -> Arduino messages
// - Search: Relative Position Array     [f"SRCH\t{cord}"]
//   - Move to point and spin in a circle
// - Collect: Relative Position Array     [f"COLL\t{cord}"]
//     - Move to point, turn on vaccum
// - Move : Follow relative angle and distance [f"MOVV\t{cord}]
// - Things found    [f"LOCT\t{cord}"]
//     -seeking approval to pick up trash
// - Toggle Vaccum: Message     [f"VACC"]

// Types of __Arduino__ -> Python
// - <x>   recieved current position from Motor Driver [f"CPOS\t{cord}]"
// - <x>   arrived at directed PT and Searching from Motor Driver f"CPOS\t{cord}]"
// - <x>   arrived at directed PT and Vaccuming f"CPOS\t{cord}]"
// - <x>   start message from UI [f"STAR\t {cord}]
// - <x>   stop messaage from UI [f"STOP\t]
// - <x>   pause message from UI [f"PAUS\t]S
// - <x>   approval to pickup object [f"OKAY\t]
// - <x>   no approval to pickup object [f"NKAY\t]



void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600); // opens serial port, sets data rate to 9600 bps
  btSerial.begin(9600); // open the bluetooth serial port

  attachInterrupt(digitalPinToInterrupt(2), RotaryChanged, CHANGE);
  attachInterrupt(digitalPinToInterrupt(3), RotaryChanged, CHANGE);

  steeringServo.attach(8); // Attach the servo
  ESC.attach(9);

  pinMode(outputPin, OUTPUT);
  digitalWrite(outputPin, HIGH);

  pinMode(bumpSensorPin, INPUT);

  attachInterrupt(digitalPinToInterrupt(bumpSensorPin), bumpSensorISR, RISING);

  center();
  armESC();

  incomingString = "";

  Command="";
  Prev="";
  Data="";
  split=-1;
  Serial_comms = 0;
  Bluetooth_comms = 0;

  CurrPos_X=0;
  CurrPos_Y=0;

  Angle = 0;
  Depth = 0;

  pinMode(0,OUTPUT);

}

//////////////CHAD FUNCTIONS ////////////////////
// void armESC() {
//   Serial.println("Arming ESC...");
//   for (int i = 0; i < 30; i++) {
//     writePWM(escPin, 1000);  // Send low PWM signal to arm ESC
//     delay(20);
//   }
//   for (int i = 0; i < 15; i++) {
//     writePWM(escPin, 1300);  // Increase PWM to start motor
//     delay(500);
//   }
//   Serial.println("ESC Armed!");
// }

void writePWM(int pin, int pulseWidth) {
  digitalWrite(pin, HIGH);
  delayMicroseconds(pulseWidth); // Pulse width determines speed
  digitalWrite(pin, LOW);
  delay(20 - pulseWidth / 1000);
}

void fwd(int it, int speed) {
  for (int i = 0; i < it; i++) {
    writePWM(escPin, speed);  // Use writePWM function to control ESC for moving forward
    delay(10);  // Delay to control speed/duration
  }
  writePWM(escPin, 0);  // Stop after iterations
}


void fwd2(int it) {
  for (int i = 0; i < it; i++) {
    writePWM(escPin, 1800);  // PWM signal for moving forward
  }
}

void steerToAngle(int angle) {
  // Normalize angle around center (42 degrees)
  int normalizedAngle = 47 + angle;
  if (normalizedAngle < 0) {
    normalizedAngle = 0;
  } else if (normalizedAngle > 110) {
    normalizedAngle = 110;
  }
  steeringServo.write(normalizedAngle); // Move servo to specified angle
  delay(5);
}


// void quickSortByDistance(TestRun arr[], int low, int high) {
//   if (low < high) {
//     // Partition the array and get the pivot index
//     int pivotIndex = partition(arr, low, high);

//     // Recursively sort elements before and after the partition
//     quickSortByDistance(arr, low, pivotIndex - 1);
//     quickSortByDistance(arr, pivotIndex + 1, high);
//   }
// }

// int partition(TestRun arr[], int low, int high) {
//   float pivot = arr[high].distance;  // Taking the last element as pivot
//   int i = low - 1;

//   for (int j = low; j < high; j++) {
//     if (arr[j].distance < pivot) {
//       i++;
//       // Swap arr[i] and arr[j]
//       TestRun temp = arr[i];
//       arr[i] = arr[j];
//       arr[j] = temp;
//     }
//   }
  
//   // Swap arr[i + 1] and arr[high] (the pivot element)
//   TestRun temp = arr[i + 1];
//   arr[i + 1] = arr[high];
//   arr[high] = temp;
  
//   return i + 1;  // Return the partition index
// }

// int getIterationsForDistanceAndSpeed(float distance, int& speed) {
//   // Sort the test data based on distance using Quick Sort
//   quickSortByDistance(testData, 0, testDataSize - 1);

//   TestRun lower = testData[0];
//   TestRun upper = testData[testDataSize - 1];
//   for (size_t i = 0; i < testDataSize - 1; i++) {
//     if (testData[i].distance <= distance && testData[i + 1].distance >= distance) {
//       lower = testData[i];
//       upper = testData[i + 1];
//       break;
//     }
//   }

//   // Linear interpolation to estimate iterations and speed
//   if (upper.distance != lower.distance) {
//     float ratio = (distance - lower.distance) / (upper.distance - lower.distance);
//     int estimatedIterations = static_cast<int>(lower.iterations + ratio * (upper.iterations - lower.iterations));
//     speed = static_cast<int>(lower.speed + ratio * (upper.speed - lower.speed));
//     return estimatedIterations;
//   }

//   return -1;
// }


// void navigateToDistanceAndAngle(float distance, int angle) {
//   steerToAngle(angle);  // Set steering to the specified angle
//   int speed;
//   int iterations = getIterationsForDistanceAndSpeed(distance, speed);
//   if (iterations != -1) {
//     fwd(iterations, speed);
//     totalDistanceDriven += distance;  // Update total distance driven
//     Serial.print("Total distance driven: ");
//     Serial.println(totalDistanceDriven);
//   } else {
//     Serial.println("Distance not found in test data");
//   }
//   center();  // Re-center the steering after movement
// }


void center() {
  steeringServo.write(47); // Move servo to center 
  delay(5);
}

void left() {
  steeringServo.write(110); // Move servo to left
  delay(5);
}

void right() {
  steeringServo.write(0); // Move servo to right
  delay(5);
}


// Interrupt Service Routine (ISR)
void bumpSensorISR() {
  
  bumpDetected = true;  // Set flag to true when bump sensor is triggered
  
  ESC.write(1550);

  while(1){
    delay(1);
  }

}



////////////////////encoder///////////////////

void armESC() {
  Serial.println("Arming ESC...");
  ESC.writeMicroseconds(1500); // Send the minimum throttle signal
  delay(3000); // Hold the low signal for 3 seconds
  Serial.println("ESC Armed!");
}

int m2s(float meters) {
    const int encoderStepsPerRevolution = 40; // Encoder steps per wheel revolution
    const float wheelDiameterMeters = 0.16002; // Wheel diameter in meters
    const float wheelCircumference = M_PI * wheelDiameterMeters; // Wheel circumference in meters

    // Calculate the number of wheel rotations for the given distance
    float wheelRotations = meters / wheelCircumference;

    // Calculate the total encoder steps (direct calculation, no gear ratio needed)
    int steps = (int)round(wheelRotations * encoderStepsPerRevolution);

    return steps;
}

int fwdCount = 0;

void runDistance(int steps) {

    Counter = 0;
    //Serial.println("Driving forward...");
    while (Counter < steps) {
      if(Serial.available() > 0  || btSerial.available() > 0){
        ESC.writeMicroseconds(1550);
        CurrPos();
        break;
      }
        if (Counter != LastCount) {
            //Serial.println(Counter);
            LastCount = Counter;
        }
        // Drive forward at a constant PWM signal
        //center();
        ESC.writeMicroseconds(1700);
    }

    // Stop the car once the target is reached
    ESC.writeMicroseconds(1550); // Stop ESC
    //Serial.println("Target distance reached!");
    GlobalCount = Counter;
    
    
}

void runDistanceRev(int steps) {
    //Serial.println("Driving forward...");
    //Serial.print("PRE SRCH REV LOOP "); Serial.print(Counter); Serial.print("  "); Serial.print(steps); Serial.println(incomingString);
    Counter = 0;
    
    while (abs(Counter) < steps) {
      if(Serial.available() > 0  || btSerial.available() > 0){
        ESC.writeMicroseconds(1550);
        CurrPos();
        break;
      }
        if (Counter != LastCount) {
            //Serial.println(Counter);
            LastCount = Counter;
        }
        // Drive forward at a constant PWM signal
        //center();
        //Serial.print("Rev loop "); Serial.println(incomingString);
        ESC.writeMicroseconds(1250);
    }

    // Stop the car once the target is reached
    ESC.writeMicroseconds(1550); // Stop ESC
    //Serial.println("Target distance reached!");
    GlobalCount = Counter;
}

void s2m(int steps) {
    const int encoderStepsPerRevolution = 40; // Encoder steps per wheel revolution
    const float wheelDiameterMeters = 0.16002; // Wheel diameter in meters
    const float wheelCircumference = M_PI * wheelDiameterMeters; // Wheel circumference in meters

    // Calculate the number of wheel rotations for the given encoder steps
    float wheelRotations = (float)steps / encoderStepsPerRevolution;

    // Calculate the distance in meters
    float meters = wheelRotations * wheelCircumference;

    Depth = meters;
    
    return;
}

void CurrPos(){
    CurrPos_X += Depth * cos(angleRadians);
    CurrPos_Y += Depth * sin(angleRadians);
}

int inch2s(float inches) {
    const int encoderStepsPerRevolution = 40; // Encoder steps per wheel revolution
    const float wheelDiameterInches = 0.16002 * 39.3701; // Wheel diameter in inches
    const float wheelCircumference = M_PI * wheelDiameterInches; // Wheel circumference in inches

    // Calculate the number of wheel rotations for the given distance
    float wheelRotations = inches / wheelCircumference;

    // Calculate the total encoder steps (direct calculation, no gear ratio needed)
    int steps = (int)round(wheelRotations * encoderStepsPerRevolution);

    return steps;
}

void SRCH(){
    // delay(3000);

    // right();
    // int steps = inch2s(100); // Calculate steps for 1 meter
    // runDistance(steps);
    // left();
    // runDistance(steps-30);
    // delay(1000);
    // runRev(steps-30);
    // right();
    // runRev(steps);
    // delay(60000);

    //delay(3000);


    right();
    int steps = inch2s(100); // Calculate steps for 1 meter
    int small = inch2s(16);
    
    runDistance(steps);
    delay(500);
    center();
    runDistanceRev(small);
    right();
    runDistanceRev(steps-80);

    center();
    runDistance(steps);
    //delay(60000);
}



//////////////////////////////////////////////

void loop() {
  digitalWrite(0,LOW);
  //Get Serial Comms from Python
  if (Serial.available() > 0 and btSerial.available() == 0) {
    // read the incoming byte:
    incomingString = Serial.readStringUntil('\n');
    
   
    //test printouts; ENCODE ARD->Py: _blahblahblah_\n (newline token message splitter)
    // Serial.print("I received in decoder: "); Serial.println(incomingString);

    //DECODING: Split String: {Command}\t{data}
    split = incomingString.indexOf('\t');
    if (split != -1)
    {
      if(Rflag == 0){
        PrevCMD = Command;
      }
      
      Command = incomingString.substring(0, split);
      
      if (split+1 < incomingString.length())  {Data = incomingString.substring(split + 1);}
      else {Data="";}
    }
    else {Command=incomingString;Data="";}


    ///// CHAD DO UR WORK HERE
    ///// YOU NEED TO ADD UR LOGIC FOR TRACKING LOCATION AND REGULARLY SEND IT TO THE UI

    //Search; Data= Angle, Depth
    if (Command == "SRCH")
    {
      //decode data: Str to Arr Int
      Data.remove(0, 1);           // Remove the first character '['
      Data.remove(Data.length() - 1, 1);  // Remove the last character ']'
      float X = Data.substring(0, Data.indexOf(', ')).toFloat();
      float Y = Data.substring(Data.indexOf(', ')+1).toFloat();
      // Serial.print("SRCH\t[");Serial.print(Angle);Serial.print(", ");Serial.print(Depth);Serial.println("]");
      Serial.print("ARDUINO received in SRCH: "); Serial.println(incomingString);

      steps = m2s(Depth);
      steps += (int)round((.03)*steps - 1.22);

      float dx = X - CurrPos_X;
        float dy = Y - CurrPos_Y;

        Depth = sqrt(dx * dx + dy * dy);

        Angle = atan2(dy, dx) * (180.0 / M_PI);

        float angleRadians = Angle * (M_PI / 180.0);
      
      
        ESC.writeMicroseconds(2000);
        steerToAngle(Angle);
        runDistance(steps);

        //Serial.print("Before recenter and SRCH "); Serial.println(incomingString);

        
        center();
        SRCH();
        //Serial.print("After recenter and SRCH "); Serial.println(incomingString);
      

      angleRadians = Angle * (M_PI / 180.0);

      // Calculate x and y positions
      CurrPos();


      Serial.print("CPOS\t[");Serial.print(CurrPos_Y);Serial.print(", ");Serial.print(CurrPos_X);Serial.println("]");
      //--------
      // Chad your code goes here
      Command = "";
      
    }

    //-----------------------------------
    //Collect trash; Data= Angle, Dept
    else if (Command == "COLL")
    {

      
      //decode data: Str to Arr Int
      Data.remove(0, 1);           // Remove the first character '['
      Data.remove(Data.length() - 1, 1);  // Remove the last character ']'
      Angle = Data.substring(0, Data.indexOf(', ')).toInt();
      Depth = Data.substring(Data.indexOf(', ')+1).toFloat();
      // Serial.print("COLL\t[");Serial.print(Angle);Serial.print(", ");Serial.print(Depth);Serial.println("]");

      Serial.print("ARDUINO received in COLL: "); Serial.println(incomingString);
      
      //--------
      // Chad your code goes here

      found = true;

      int steps = m2s(Depth);
      steps += (int)round((.03)*steps - 1.22);
      steerToAngle(Angle);

      runDistance(steps);
      center();

      float angleRadians = Angle * (M_PI / 180.0);

      center();

      // Calculate x and y positions
      CurrPos();

      digitalWrite(0,HIGH);

      Serial.print("CPOS\t[");Serial.print(CurrPos_Y);Serial.print(", ");Serial.print(CurrPos_X);Serial.println("]");

        //return home?
      // center();
      // runDistanceRev(GlobalCount - steps);      
      Command = "";
    }

    else if (Command == "MOVE")
    {
      //decode data: Str to Arr Int
      Data.remove(0, 1);           // Remove the first character '['
      Data.remove(Data.length() - 1, 1);  // Remove the last character ']'
      Angle = Data.substring(0, Data.indexOf(', ')).toInt();
      Depth = Data.substring(Data.indexOf(', ')+1).toFloat();
      // Serial.print("COLL\t[");Serial.print(Angle);Serial.print(", ");Serial.print(Depth);Serial.println("]");
      Serial.print("ARDUINO received in MOV: "); Serial.println(incomingString);

      center();

      
      //--------
      // Chad your code goes here


      // for(float dist = Depth; dist > -1; dist--){
      //   if (Serial.available() == 0 and btSerial.available() == 0){
      //       int steps = m2s(Depth - dist);
      //       steerToAngle(Angle);
      //       runDistance(steps);

      //       float angleRadians = Angle * (M_PI / 180.0);

      //       // Calculate x and y positions
      //       CurrPos_X += Depth * cos(angleRadians);
      //       CurrPos_Y += Depth * sin(angleRadians);

      //   }
      //   else{
      //       break;
      //   }
      // }

        int steps = m2s(Depth);
        steps += (int)round((.03)*steps - 1.22);
        steerToAngle(Angle);
        runDistance(steps);

        center();

        float angleRadians = Angle * (M_PI / 180.0);

        // Calculate x and y positions
        CurrPos();

        Serial.print("CPOS\t[");Serial.print(CurrPos_Y);Serial.print(", ");Serial.print(CurrPos_X);Serial.println("]");

      
                Command = "";

    }


    else if (Command == "RTUN")
    {
      //decode data: Str to Arr Int
      Data.remove(0, 1);           // Remove the first character '['
      Data.remove(Data.length() - 1, 1);  // Remove the last character ']'
      float X = Data.substring(0, Data.indexOf(', ')).toFloat();
      float Y = Data.substring(Data.indexOf(', ')+1).toFloat();
      // Serial.print("COLL\t[");Serial.print(Angle);Serial.print(", ");Serial.print(Depth);Serial.println("]");
      Serial.print("I received in MOV: "); Serial.println(incomingString);

      
      //--------
      // Chad your code goes here


      // for(float dist = Depth; dist > -1; dist--){
      //   if (Serial.available() == 0 and btSerial.available() == 0){
      //       int steps = m2s(Depth - dist);
      //       steerToAngle(Angle);
      //       runDistance(steps);

      //       float angleRadians = Angle * (M_PI / 180.0);

      //       // Calculate x and y positions
      //       CurrPos_X += Depth * cos(angleRadians);
      //       CurrPos_Y += Depth * sin(angleRadians);

      //   }
      //   else{
      //       break;
      //   }
      // }



        float dx = X - CurrPos_X;
        float dy = Y - CurrPos_Y;

        Depth = sqrt(dx * dx + dy * dy);

        Angle = atan2(dy, dx) * (180.0 / M_PI);

        float angleRadians = Angle * (M_PI / 180.0);

        int steps = m2s(Depth);
        steps += (int)round((.03)*steps - 1.22);
        steerToAngle(Angle);
        runDistanceRev(steps);

        center();

        // // Calculate x and y positions
        // CurrPos_X += Depth * cos(angleRadians);
        // CurrPos_Y += Depth * sin(angleRadians);

        Serial.print("CPOS\t[");Serial.print(CurrPos_Y);Serial.print(", ");Serial.print(CurrPos_X);Serial.println("]");
      Command = "";
                

    }
    else if (Command == "PAUS")
    {
      //decode data: Str to Arr Int
      Data.remove(0, 1);           // Remove the first character '['
      Data.remove(Data.length() - 1, 1);  // Remove the last character ']'
      Angle = Data.substring(0, Data.indexOf(', ')).toInt();
      Depth = Data.substring(Data.indexOf(', ')+1).toFloat();
      // Serial.print("COLL\t[");Serial.print(Angle);Serial.print(", ");Serial.print(Depth);Serial.println("]");
      Serial.print("I received in MOV: "); Serial.println(incomingString);

      
      //--------
      // Chad your code goes here
      
      if(Rflag == 0){
        ESC.writeMicroseconds(1550);
        Rflag = !Rflag;
      }
      else if(Rflag == 1 ){
        Command = PrevCMD;
        Rflag = !Rflag;
      }

      Serial.print("CPOS\t[");Serial.print(CurrPos_Y);Serial.print(", ");Serial.print(CurrPos_X);Serial.println("]");

      Command = "";     

    }
    else if (Command == "STOP")
    {
      //decode data: Str to Arr Int
      Data.remove(0, 1);           // Remove the first character '['
      Data.remove(Data.length() - 1, 1);  // Remove the last character ']'
      Angle = Data.substring(0, Data.indexOf(', ')).toInt();
      Depth = Data.substring(Data.indexOf(', ')+1).toFloat();
      // Serial.print("COLL\t[");Serial.print(Angle);Serial.print(", ");Serial.print(Depth);Serial.println("]");
      //Serial.print("I received in MOV: "); Serial.println(incomingString);

      
      //--------
      // Chad your code goes here


      // for(float dist = Depth; dist > -1; dist--){
      //   if (Serial.available() == 0 and btSerial.available() == 0){
      //       int steps = m2s(Depth - dist);
      //       steerToAngle(Angle);
      //       runDistance(steps);

      //       float angleRadians = Angle * (M_PI / 180.0);

      //       // Calculate x and y positions
      //       CurrPos_X += Depth * cos(angleRadians);
      //       CurrPos_Y += Depth * sin(angleRadians);

      //   }
      //   else{
      //       break;
      //   }
      // }

      ESC.write(1550);
      Serial.print("CPOS\t[");Serial.print(CurrPos_X);Serial.print(", ");Serial.print(CurrPos_Y);Serial.println("]");

      Command = "";
                

    }



    //-----------------------------------
    //Send message to App from Python
    else if (Command == "WIRE")
    {
      btSerial.println(incomingString); //NOTE: whats the encode for Ard->Blueetooth (ln or nah)????????????????????????
    }
    //-----------------------------------
    //Toggle!!! Vaccum

    /* Phased out */
    // else if (Command == "VACC")
    // {
    //   //--------
    //   // Chad your code goes here
    //   // This doesnt exist yet
    //   continue;
    // }    
  
    Serial_comms = 1;
  }

///// CHAD DO NOT WORK BELOW HERE THIS IS LAURENS STUFF vvvv
  //Get Bluetooth Comms from App
  if(btSerial.available() > 0 ){
    String incomingString  = btSerial.readStringUntil('\n');
  
    //-----------------------------------
    //STOP,PAUSE messages to App from Python
    if (incomingString.substring(0,4) == "STOP" or incomingString.substring(0,4)== "PAUS" or incomingString.substring(0,4) == "OKAY" or incomingString.substring(0,4) == "NKAY")
    {
      Serial.println(incomingString.substring(0,4) + "\t"); //NOTE: whats the encode for Ard->Blueetooth 
    }

    else if (incomingString.substring(0,2) == "C1"){
        C1 = incomingString.substring(3,incomingString.length());
    }
    
    else if(incomingString.substring(0,2)== "C2"){
        C2 = incomingString.substring(3,incomingString.length());


    } 
     else if(incomingString.substring(0,2)== "C3"){
        C3 = incomingString.substring(3,incomingString.length());


    } 
    else if(incomingString.substring(0,2) == "C4"){
      C4 = incomingString.substring(3,incomingString.length());
      if (!(C1 == "" or C2 == "" or C3 =="" or C4 == "")){
      Serial.print("STAR\t");
      Serial.print(C1 + ":");
      Serial.print(C2 + ":");
      Serial.print(C3 + ":");
      Serial.print(C4 + "\n");
      }
      C1 = "";
      C2 = "";
      C3 = "";
      C4 = "";
     
      
  }
    //----------------------------------- 
}
}
