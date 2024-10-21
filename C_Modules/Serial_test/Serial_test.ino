

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600); // opens serial port, sets data rate to 9600 bps
	// Serial.setTimeout(1); 

}



void loop() {
  // send data only when you receive data:
  if (Serial.available() > 0) {
    
    // read the incoming byte:
    String incomingString = Serial.readStringUntil('\n');

    // prints the received data
    // Serial.print("I received: ");
    // Serial.println(incomingString);
    // Serial.print(incomingString);


    // Split String: {Command}\t{data}
    String Command = incomingString.substring(0, incomingString.indexOf('\t'));
    String Data = incomingString.substring(incomingString.indexOf('\t') + 1);




    //USING GIVEN COMMAND
    if (Command == "SRCH")
    {
      //!!!!!!!!SEARCH COMMAND: Move to point

      //decode data: Str to Arr Int
      Data.remove(0, 1);           // Remove the first character '['
      Data.remove(Data.length() - 1, 1);  // Remove the last character ']'
      float x = Data.substring(0, Data.indexOf(', ')).toFloat();
      float y = Data.substring(Data.indexOf(', ')+1).toFloat();
      
      // Serial.print("SRCH: ");Serial.print(x);Serial.print(", ");Serial.print(y);Serial.println("");
      Serial.print("Commanded to Search: @");Serial.print(x);Serial.print(", ");Serial.print(y);Serial.println("");


      //------------------------------
      // Chad your code goes here
    }
    else if (Command == "COLL")
    {
      //!!!!!!!!COLLECT TRASH COMMAND: Move to point, turn on vaccum

      //decode data: Str to Arr Int
      Data.remove(0, 1);           // Remove the first character '['
      Data.remove(Data.length() - 1, 1);  // Remove the last character ']'
      float x = Data.substring(0, Data.indexOf(', ')).toFloat();
      float y = Data.substring(Data.indexOf(', ')+1).toFloat();
      
      // Serial.print("COLL: ");Serial.print(x);Serial.print(", ");Serial.print(y);Serial.println("");
      Serial.print("Commanded to Collect: @");Serial.print(x);Serial.print(", ");Serial.print(y);Serial.println("");


      //------------------------------
      // Chad your code goes here
    }
    else if (Command == "WIRE")
    {
      //!!!!!!!!WIRELESS COMMAND: Send data



      //------------------------------
      // Chad your code goes here
    }
    else
    {
      Serial.println(incomingString);
    }


  }
  
}
