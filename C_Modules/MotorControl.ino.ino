/*  MotorControl.ino
    This file is responsible for handling all drive
    commands for our WALLE bot.
*/
#include <Servo.h>
#include <Vector.h>


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

// Define a static-sized array instead of Vector
TestRun testData[] = {
  {10.0, 300, 1500},
  {5.0, 150, 1200},
  {1.0, 30, 1100}
};

// Calculate the size of the array
const int testDataSize = sizeof(testData) / sizeof(testData[0]);

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

void quickSortByDistance(TestRun arr[], int low, int high) {
  if (low < high) {
    // Partition the array and get the pivot index
    int pivotIndex = partition(arr, low, high);

    // Recursively sort elements before and after the partition
    quickSortByDistance(arr, low, pivotIndex - 1);
    quickSortByDistance(arr, pivotIndex + 1, high);
  }
}

int partition(TestRun arr[], int low, int high) {
  float pivot = arr[high].distance;  // Taking the last element as pivot
  int i = low - 1;

  for (int j = low; j < high; j++) {
    if (arr[j].distance < pivot) {
      i++;
      // Swap arr[i] and arr[j]
      TestRun temp = arr[i];
      arr[i] = arr[j];
      arr[j] = temp;
    }
  }
  
  // Swap arr[i + 1] and arr[high] (the pivot element)
  TestRun temp = arr[i + 1];
  arr[i + 1] = arr[high];
  arr[high] = temp;
  
  return i + 1;  // Return the partition index
}



int getIterationsForDistanceAndSpeed(float distance, int& speed) {
  // Sort the test data based on distance using Quick Sort
  quickSortByDistance(testData, 0, testDataSize - 1);

  TestRun lower = testData[0];
  TestRun upper = testData[testDataSize - 1];
  for (size_t i = 0; i < testDataSize - 1; i++) {
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
    float distanceToDrive = 10;   //example values
    int angleToSteer = 6;         // ""

    navigateToDistanceAndAngle(distanceToDrive, angleToSteer);  // Navigate based on camera input
  } else {
    // Stop due to bumper trigger
    delay(1000);
    bumperTriggered = false;
  }
}
