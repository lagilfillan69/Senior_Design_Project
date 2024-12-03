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

// NOTE :  We cannot move more than 47 degree either way
void steerToAngle(int angle) {
  // Normalize angle around center (42 degrees)
  int normalizedAngle = 47 + angle;
  if (normalizedAngle < 0) {
    normalizedAngle = 0;
  } else if (normalizedAngle > 110) {
    normalizedAngle = 110;
  }
  steeringServo.write(normalizedAngle); // Move servo to specified angle
  Steering_Angle = angle;
  delay(5);
}

void center() {
  steeringServo.write(47); // Move servo to center 
  Steering_Angle = 0
  delay(5);
}

// TODO CHAD

void left() {
  steeringServo.write(110); // Move servo to left
  Steering_Angle = 63// NORMALIZED
  delay(5);
}

void right() {
  steeringServo.write(0); // Move servo to right
  steering_Angle = -47  // NEED TO NOrMALIZED
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
    int local_counter = Counter;
  
    while (Counter - local_counter < steps) {
      if(Serial.available() > 0  || btSerial.available() > 0){
        bicycle_equation(); // Updates location
        ESC.writeMicroseconds(1550);
        break;
      }
      
        // Drive forward at a constant PWM signal
        //center();
        //Update 
        ESC.writeMicroseconds(1700);
         // Updates location
    }

    // Stop the car once the target is reached
    ESC.writeMicroseconds(1550); // Stop ESC
    bicycle_equation();
    //Serial.println("Target distance reached!");
    // GlobalCount = Counter;
    
    
}

void runDistanceRev(int steps) {
    //Serial.println("Driving forward...");
    //Serial.print("PRE SRCH REV LOOP "); Serial.print(Counter); Serial.print("  "); Serial.print(steps); Serial.println(incomingString);
    local_counter = Counter;
    
    while (abs(Counter - local_counter) < steps) {
      if(Serial.available() > 0  || btSerial.available() > 0){
        ESC.writeMicroseconds(1550);
        bicycle_equation();
        break;
      }
    
        // Drive forward at a constant PWM signal
        //center();
        //Serial.print("Rev loop "); Serial.println(incomingString);
        ESC.writeMicroseconds(1250);
        
    }

    // Stop the car once the target is reached
    ESC.writeMicroseconds(1550); // Stop ESC
    bicycle_equation();
    //Serial.println("Target distance reached!");
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

// void CurrPos(){
//     CurrPos_X += Depth * cos(angleRadians);
//     CurrPos_Y += Depth * sin(angleRadians);
// }

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

    //LOCATION IS UPDATED IN RUN DISTANCE / REV
    //delay(60000);
}

float degree_to_rad(float rad){
  return rad*180/PI;
}

float bicycle_equation(){
    
    float delta_s = (Counts - Previous_Steer_Count / COUNTS_PER_REV) * wheel_circumference;
    
    Previous_Steer_Count = Counts;
    // Read steering angle δ in radians
    float delta = degree_to_rad(Steering_Angle)

    // Adjust steering angle due to understeer caused by locked differentials
    float effective_delta = delta * UNDERSTEER_COEFF;

    // Compute curvature κ = tan(δ) / L
    float curvature = tan(delta) / WHEELBASE;

    // Compute change in heading angle Δθ = κ * Δs
    float delta_theta = curvature * delta_s;

    // Update position
    float theta_mid = theta + (delta_theta / 2.0f);
    CurrPos_X += delta_s * cos(theta_mid);
    CurrPos_Y += delta_s * sin(theta_mid);
}


