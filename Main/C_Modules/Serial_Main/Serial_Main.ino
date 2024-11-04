#include <SoftwareSerial.h>
SoftwareSerial btSerial(4,3);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600); // opens serial port, sets data rate to 9600 bps
  btSerial.begin(9600); // open the bluetooth serial port
	// Serial.setTimeout(1);
  String Command="";
  String Data="";
  int split=-1;
  int Serial_comms = 0;
  int Bluetooth_comms = 0;

  float CurrPos_X=0;
  float CurrPos_Y=1;

  float Angle = 0;
  float Depth = 0;

}



void loop() {

  //Get Serial Comms from Python
  if (Serial.available() > 0 and btSerial.available() == 0) {
    // read the incoming byte:
    String incomingString = Serial.readStringUntil('\n');
    String Command = "";
    //test printouts; ENCODE ARD->Py: _blahblahblah_\n (newline token message splitter)
    // Serial.print("I received: "); Serial.println(incomingString);

    //DECODING: Split String: {Command}\t{data}
    int split = incomingString.indexOf('\t');
    if (split != -1)
    {
      Command = incomingString.substring(0, split);
      if (split+1 < incomingString.length())  {Data = incomingString.substring(split + 1);}
      else {Data=""}
    }
    else {Command=incomingString;Data="";}
  
    Serial_comms = 1;
  }

  //Get Bluetooth Comms from App
  if(btSerial.available() > 0 ){
    String incomingString  = btSerial.readStringUntil('\n');
    // Split String: {Command}\t{data}
    String split = incomingString.indexOf('\t')
    if (split != -1)
    {
      Command = incomingString.substring(0, split);
      if (split+1 < incomingString.length())  {Data = incomingString.substring(split + 1);}
      else {Data=""}
    }
    else
     {
      split = incomingString.indexof(':');
      if (split != -1){
        Command = incomingString.substring(0, split);
         if (split+1 < incomingString.length())  {Data = incomingString.substring(split + 1);}
        else {Data="";}
      }
      else{Command=incomingString;Data="";}
      }
    Bluetooth_comms = 1;
  }



  //========================================================
  //Using Comms

  /*
    In State 5, where waiting for approval:
    to approve:   Serial.println("OKAY")
    to not:       Serial.println("NKAY")

    When arrived at point
    Serial.print("ARSR\t[");Serial.print(CurrPos_X);Serial.print(", ");Serial.print(CurrPos_Y);Serial.println("]");
  */




  //-----------------------------------
  //Python to Arduino !!!!!!
  if (Serial_comms==1)
  {
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
      btSerial.println(incomingString) //NOTE: whats the encode for Ard->Blueetooth (ln or nah)????????????????????????
    }
    //-----------------------------------
    //Toggle!!! Vaccum
    else if (Command == "VACC")
    {
      //--------
      // Chad your code goes here
    }    
    Serial_comms = 0;
  }




  //----------------------------------------------------------------------
  // Bluetooth to Arduino to Python !!!!!!

  else if (Bluetooth_comms==1)
  {
    //START Message from App; Data=
    else if (Command == "STAR" and Bluetooth_comms==1)
    {

      Serial.print("STAR\t");Serial.print(Data);
    }

    //-----------------------------------
    //STOP,PAUSE messages to App from Python
    else if (Command == "STOP" or Command == "PAUS" or Command == "OKAY" or Command == "NKAY" or)
    {
      Serial.println(Command + "\t") //NOTE: whats the encode for Ard->Blueetooth 
    }

    //-----------------------------------
    //Send over message from Bluetooth to Python; data=Message
    else if (Command == "RECV")
    {
      Serial.print("RECV\t");Serial.print(Data); //NOTE: whats the encode for Ard->Blueetooth (ln or nah)????????????????????????
    }

    else if (Command == "C1" or Command == 'C2' or Command == 'C3')
      Serial.print(Data)

    //-----------------------------------
  
  //THIS SHOULD BE INTERNAL
  //give current position [f"CPOS\t{cord}"]
  else if (Command == "CPOS")
  {
    Serial.print("CPOS\t[");Serial.print(CurrPos_X);Serial.print(", ");Serial.print(CurrPos_Y);Serial.println("]");
  }

    
    Bluetooth_comms = 0;
  }



  
}
