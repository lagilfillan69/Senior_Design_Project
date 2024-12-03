#include "RotaryEncoder.h"
#include <Servo.h>


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

/// NEW GLOBAL VARIBLE FOR ANGLE
int Previous_Steer_Count = 0;
int Steering_Angle = 0;


 // Constants (adjust these according to your RC car's specifications)
const float WHEEL_DIAMETER = 0.16002;  // Wheel diameter in meters (example: 5 cm)
const int COUNTS_PER_REV = 20;      // Encoder counts per wheel revolution
const float WHEELBASE = .405;        // Distance between front and rear axles in meters
const float UNDERSTEER_COEFF = 0.8;
float wheel_circumference = M_PI * WHEEL_DIAMETER;

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
float theta=0.0;

int steps = 0;

float angleRadians = 0;

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
