/*  MotorControl.ino
    This file is responsible for handling all drive
    commands for our WALLE bot.
*/
#include <Servo.h>
#include <ArduinoSTL.h>
#include <Vector.h>
#include <algorithm>
#include <cmath>

// Servo and motor control pins
Servo steeringServo;
const int escPin = 9;
const int bumpSensor = 2;  // Assigning pin for bump sensor

volatile bool bumperTriggered = false;
float totalDistanceDriven = 0.0;  // Variable to keep track of total distance driven

// Struct to store test data
struct TestRun {
  float distance;
  int iterations;
  int speed;
};

std::vector<TestRun> testData = {
  //{distance, iterations, speed}
  {10.0, 300, 1500},
  {5.0, 150, 1200},
  {1.0, 30, 1100}
};

// Steering functions
void center() {
  steeringServo.write(42); // Move servo to center 
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

void steerToAngle(int angle) {
  // Normalize angle around center (42 degrees)
  int normalizedAngle = 42 + angle;
  if (normalizedAngle < 0) {
    normalizedAngle = 0;
  } else if (normalizedAngle > 110) {
    normalizedAngle = 110;
  }
  steeringServo.write(normalizedAngle); // Move servo to specified angle
  delay(5);
}

// Write PWM signal to motor control
void writePWM(int pin, int pulseWidth) {
  digitalWrite(pin, HIGH);
  delayMicroseconds(pulseWidth); // Pulse width determines speed
  digitalWrite(pin, LOW);
  delay(20 - pulseWidth / 1000);
}

// Drivetrain control functions
void fwd(int it, int speed) {
  for (int i = 0; i < it; i++) {
    writePWM(escPin, speed);  // Use writePWM function to control ESC for moving forward
    delay(10);  // Delay to control speed/duration
  }
  writePWM(escPin, 0);  // Stop after iterations
}

void fwd2(int it, int speed) {
  for (int i = 0; i < it; i++) {
    writePWM(escPin, speed);  // Use writePWM function to control ESC for moving forward
    delay(10);
  }
  writePWM(escPin, 0);  // Stop after iterations
}

int getIterationsForDistanceAndSpeed(float distance, int& speed) {
  for (const auto& test : testData) {
    if (test.distance == distance) {
      speed = test.speed;
      return test.iterations;
    }
  }

  // Sorting the test data based on distance to find the lower and upper bounds
  std::sort(testData.begin(), testData.end(), [](const TestRun& a, const TestRun& b) {
    return a.distance < b.distance;
  });

  TestRun lower = testData.front();
  TestRun upper = testData.back();
  for (size_t i = 0; i < testData.size() - 1; i++) {
    if (testData[i].distance <= distance && testData[i + 1].distance >= distance) {
      lower = testData[i];
      upper = testData[i + 1];
      break;
    }
  }

  // Linear interpolation to estimate iterations and speed
  if (upper.distance != lower.distance) {
    float ratio = (distance - lower.distance) / (upper.distance - lower.distance);
    int estimatedIterations = static_cast<int>(lower.iterations + ratio * (upper.iterations - lower.iterations));
    speed = static_cast<int>(lower.speed + ratio * (upper.speed - lower.speed));
    return estimatedIterations;
  }

  return -1;
}

void navigateToDistance(float distance) {
  int speed;
  int iterations = getIterationsForDistanceAndSpeed(distance, speed);
  if (iterations != -1) {
    fwd(iterations, speed);
    totalDistanceDriven += distance;  // Update total distance driven
    Serial.print("Total distance driven: ");
    Serial.println(totalDistanceDriven);
  } else {
    Serial.println("Distance not found in test data");
  }
}

void navigateToDistanceAndAngle(float distance, int angle) {
  steerToAngle(angle);  // Set steering to the specified angle
  int speed;
  int iterations = getIterationsForDistanceAndSpeed(distance, speed);
  if (iterations != -1) {
    fwd(iterations, speed);
    totalDistanceDriven += distance;  // Update total distance driven
    Serial.print("Total distance driven: ");
    Serial.println(totalDistanceDriven);
  } else {
    Serial.println("Distance not found in test data");
  }
  center();  // Re-center the steering after movement
}

void bumpSensorInterrupt() {
  bumperTriggered = true;  // Set flag when bump sensor is triggered
  writePWM(escPin, 0);  // Stop the bot immediately
}

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

void setup() {
  // Initialize serial communication
  Serial.begin(9600);

  // Attach the steering servo
  steeringServo.attach(3);  // Assuming servo is connected to pin 3
  center();  // Center the steering at startup

  // Set up the ESC pin
  pinMode(escPin, OUTPUT);
  analogWrite(escPin, 0);  // Ensure motor is stopped initially

  // Set up the bump sensor pin
  pinMode(bumpSensor, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(bumpSensor), bumpSensorInterrupt, FALLING);

  // Arm the ESC
  armESC();
}

// void loop() {
//   if (!bumperTriggered) {
//     // Example navigation command
//     navigateToDistanceAndAngle(5.0, 70);  // Navigate 5 feet forward while steering at 70 degrees
//   } else {
//     Serial.println("Bumper triggered! Stopping the robot.");
//     delay(1000);  // Wait for a second before resetting
//     bumperTriggered = false;  // Reset the bumper trigger flag
//   }
// }

void loop() {
  if (!bumperTriggered) {
    // Assuming distance and angle values are updated by an external camera system
    float distanceToDrive = 10;  // Hypothetical function to get distance
    int angleToSteer = 6;          // Hypothetical function to get angle

    navigateToDistanceAndAngle(distanceToDrive, angleToSteer);  // Navigate based on camera input
  } else {
    // Stop due to bumper trigger
    delay(1000);
    bumperTriggered = false;
  }
}
