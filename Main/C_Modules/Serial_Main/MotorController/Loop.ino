#include <SoftwareSerial.h>
/* Chad stuff */
#include "RotaryEncoder.h"
#include <Servo.h>
#include <Vector.h>


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

        //Serial.print("Before recenter and SRCH "); Serial.println(incomingString)
        center();
        SRCH();
        //Serial.print("After recenter and SRCH "); Serial.println(incomingString);
      

      angleRadians = Angle * (M_PI / 180.0);


      //Should only be done in functions associated with movememnt
      // // Calculate x and y positions
      // CurrPos();


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
      Serial.print("I received in PAUS: "); Serial.println(incomingString);

      
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