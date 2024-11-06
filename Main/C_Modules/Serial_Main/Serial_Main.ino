#include <SoftwareSerial.h>
SoftwareSerial btSerial(4,3);
int escPin = 9;

String Command;
String Data;
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



  //========================================================
  //Using Comms

  /*
    In State 5, where waiting for approval:
    to approve:   Serial.println("OKAY")
    to not:       Serial.println("NKAY")

    When arrived at point
    Serial.print("ARSR\t[");Serial.print(CurrPos_X);Serial.print(", ");Serial.print(CurrPos_Y);Serial.println("]");
  */

// '''
// Types of __Python__ -> Arduino messages
// - Search: Relative Position Array     [f"SRCH\t{cord}"]
//   - Move to point and spin in a circle
// - Collect: Relative Position Array     [f"COLL\t{cord}"]
//     - Move to point, turn on vaccum
// - Things found    [f"LOCT\t{cord}"]
//     -seeking approval to pick up trash
// - Toggle Vaccum: Message     [f"VACC"]

// Types of __Arduino__ -> Python
// - <x>   recieved current position from Motor Driver [f"CPOS\t{cord}]"
// - <x>   arrived at directed PT and Searching from Motor Driver f"ARSR\t{cord}]"
// - <x>   arrived at directed PT and Vaccuming f"ARSR\t{cord}]"
// - <x>   start message from UI [f"STAR\t {cord}]
// - <x>   stop messaage from UI [f"STOP\t]
// - <x>   pause message from UI [f"PAUS\t]S
// - <x>   approval to pickup object [f"OKAY\t]
// - <x>   no approval to pickup object [f"NKAY\t]



void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600); // opens serial port, sets data rate to 9600 bps
  btSerial.begin(9600); // open the bluetooth serial port
	// Serial.setTimeout(1);
  armESC();
  Command="";
  Data="";
  split=-1;
  Serial_comms = 0;
  Bluetooth_comms = 0;

  CurrPos_X=0;
  CurrPos_Y=1;

  Angle = 0;
  Depth = 0;

}

//////////////CHAD FUNCTIONS ////////////////////
void armESC() {
  Serial.println("Arming ESC...");
  for (int i = 0; i < 30; i++) {
    writePWM(escPin, 1000);  // Send low PWM signal to arm ESC
    delay(20);
  }
  for (int i = 0; i < 15; i++) {
    writePWM(escPin, 1300);  // Increase PWM to start motor
    delay(500);
  }
  Serial.println("ESC Armed!");
}

void writePWM(int pin, int pulseWidth) {
  digitalWrite(pin, HIGH);
  delayMicroseconds(pulseWidth); // Pulse width determines speed
  digitalWrite(pin, LOW);
  delay(20 - pulseWidth / 1000);
}

void fwd2(int it) {
  for (int i = 0; i < it; i++) {
    writePWM(escPin, 1800);  // PWM signal for moving forward
  }
}
//////////////////////////////////////////////

void loop() {

  //Get Serial Comms from Python
  if (Serial.available() > 0 and btSerial.available() == 0) {
    // read the incoming byte:
    String incomingString = Serial.readStringUntil('\n');
   
    //test printouts; ENCODE ARD->Py: _blahblahblah_\n (newline token message splitter)
    // Serial.print("I received: "); Serial.println(incomingString);

    //DECODING: Split String: {Command}\t{data}
    split = incomingString.indexOf('\t');
    if (split != -1)
    {
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
      Angle = Data.substring(0, Data.indexOf(', ')).toFloat();
      Depth = Data.substring(Data.indexOf(', ')+1).toFloat();
      // Serial.print("SRCH\t[");Serial.print(Angle);Serial.print(", ");Serial.print(Depth);Serial.println("]");


      //--------
      // Chad your code goes here
    }

    //-----------------------------------
    //Collect trash; Data= Angle, Dept
    else if (Command == "COLL")
    {
      //decode data: Str to Arr Int
      Data.remove(0, 1);           // Remove the first character '['
      Data.remove(Data.length() - 1, 1);  // Remove the last character ']'
      Angle = Data.substring(0, Data.indexOf(', ')).toFloat();
      Depth = Data.substring(Data.indexOf(', ')+1).toFloat();
      // Serial.print("COLL\t[");Serial.print(Angle);Serial.print(", ");Serial.print(Depth);Serial.println("]");


      //--------
      // Chad your code goes here
    }

    //-----------------------------------
    //Send message to App from Python
    else if (Command == "WIRE")
    {
      btSerial.println(incomingString); //NOTE: whats the encode for Ard->Blueetooth (ln or nah)????????????????????????
    }
    //-----------------------------------
    //Toggle!!! Vaccum
    else if (Command == "VACC")
    {
      //--------
      // Chad your code goes here
    }    
  
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
      Serial.println(Command + "\t"); //NOTE: whats the encode for Ard->Blueetooth 
    }

    else if (incomingString.substring(0,2) == "C1" {
        C1 = incomingString.substring(3,incomingString.length);
      
    }
    
    else if(incomingString.substring(0,2)== "C2"){
        C2 = incomingString.substring(3,incomingString.length);


    } 
    else if(incomingString.substring(0,2) == 'C3'){
      C3 = incomingString.substring(3,incomingString.length);

      Serial.print("STAR \t");
      Serial.print(C1 + ":")
      Serial.print(C2 + ":")
      Serial.print(C3 + "\n") 

      C1 = "";
      C2 = "";
      C3 = "";
      
    }
    //----------------------------------- 
}
