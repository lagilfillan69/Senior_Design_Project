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
  Steering_Angle = 0;
  delay(5);
}

// TODO CHAD

void left() {
  steeringServo.write(110); // Move servo to left
  Steering_Angle = 63;// NORMALIZED
  delay(5);
}

void right() {
  steeringServo.write(0); // Move servo to right
  Steering_Angle = -47;  // NEED TO NOrMALIZED
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
    int local_counter = Counter;
    
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
    
    float delta_s = (Counter - Previous_Steer_Count / COUNTS_PER_REV) * wheel_circumference;
    
    Previous_Steer_Count = Counter;
    // Read steering angle δ in radians
    float delta = degree_to_rad(Steering_Angle);

    // Adjust steering angle due to understeer caused by locked differentials
    float effective_delta = delta * UNDERSTEER_COEFF;

    // Compute curvature κ = tan(δ) / L
    float curvature = tan(delta) / WHEELBASE;

    // Compute change in heading angle Δθ = κ * Δs
    float delta_theta = curvature * delta_s;

    //     // Update heading angle
    theta += delta_theta;

    // Normalize theta to be within [-π, π]
    if (theta > PI)
        theta -= 2.0f * PI;
    else if (theta < -PI)
        theta += 2.0f * PI;

    // Update position
    float theta_mid = theta + (delta_theta / 2.0f);
    CurrPos_X += delta_s * cos(theta_mid);
    CurrPos_Y += delta_s * sin(theta_mid);
}

float bicycle_equation_bckwrd(){
    float delta_s = (Counter - Previous_Steer_Count / COUNTS_PER_REV) * wheel_circumference;
    
    Previous_Steer_Count = Counter;
    // Read steering angle δ in radians
    float delta = degree_to_rad(Steering_Angle);

    // Adjust steering angle due to understeer caused by locked differentials
    float effective_delta = delta * UNDERSTEER_COEFF_BCK;

    // Compute curvature κ = tan(δ) / L
    float curvature = tan(delta) / WHEELBASE;

    // Compute change in heading angle Δθ = κ * Δs
    float delta_theta = curvature * delta_s;

    //     // Update heading angle
    theta += delta_theta;

    // Normalize theta to be within [-π, π]
    if (theta > PI)
        theta -= 2.0f * PI;
    else if (theta < -PI)
        theta += 2.0f * PI;

    // Update position
    float theta_mid = theta + (delta_theta / 2.0f);
    CurrPos_X += delta_s * cos(theta_mid);
    CurrPos_Y += delta_s * sin(theta_mid);
}



// float bicycle_equationREV(){
    
//     float delta_s = (Counter - Previous_Steer_Count / COUNTS_PER_REV) * wheel_circumference;
    
//     Previous_Steer_Count = Counter;
//     // Read steering angle δ in radians
//     float delta = degree_to_rad(Steering_Angle);

//     // Adjust steering angle due to understeer caused by locked differentials
//     float effective_delta = delta * UNDERSTEER_COEFF;

//     // Compute curvature κ = tan(δ) / L
//     float curvature = tan(delta) / WHEELBASE;

//     // Compute change in heading angle Δθ = κ * Δs
//     float delta_theta = curvature * delta_s;

//     //     // Update heading angle
//     theta += delta_theta;

//     // Normalize theta to be within [-π, π]
//     if (theta > PI)
//         theta -= 2.0f * PI;
//     else if (theta < -PI)
//         theta += 2.0f * PI;

//     // Update position
//     float theta_mid = theta + (delta_theta / 2.0f);
//     CurrPos_X += delta_s * cos(theta_mid);
//     CurrPos_Y += delta_s * sin(theta_mid);
// }

// void inverse_bicycle_equation(float Target_X, float Target_Y) {
//     // Compute change in position
//     float delta_x = Target_X - CurrPos_X;
//     float delta_y = Target_Y - CurrPos_Y;
    
//     // Compute distance to move
//     float delta_s = sqrt(delta_x * delta_x + delta_y * delta_y);
    
//     // Compute change in heading angle
//     float phi = atan2(delta_y, delta_x);
//     float delta_theta = 2.0f * (phi - theta);
    
//     // Normalize delta_theta to be within [-π, π]
//     if (delta_theta > PI)
//         delta_theta -= 2.0f * PI;
//     else if (delta_theta < -PI)
//         delta_theta += 2.0f * PI;
    
//     // Compute effective steering angle
//     float numerator = delta_theta * WHEELBASE;
//     float denominator = delta_s;
    
//     if (denominator == 0) {
//         // Avoid division by zero
//         effective_delta = 0;
//     } else {
//         float effective_delta = atan2(numerator, denominator);
//     }
    
//     // Compute actual steering angle, accounting for understeer
//     float delta = effective_delta / UNDERSTEER_COEFF;
    
//     // Convert steering angle to degrees
//     Steering_Angle = rad_to_degree(delta);
    
//     // Compute required wheel steps (or counts)
//     float delta_steps = (delta_s / wheel_circumference) * COUNTS_PER_REV;
//     Steps = Previous_Steer_Count + delta_steps;
    


//     // // Update Previous_Steer_Count for next iteration
//     // Previous_Steer_Count = Counter;
  
//     // // Update heading angle
//     // theta += delta_theta;
    
//     // // Normalize theta to be within [-π, π]
//     // if (theta > PI)
//     //     theta -= 2.0f * PI;
//     // else if (theta < -PI)
//     //     theta += 2.0f * PI;
    
//     // // Update position
//     // /// SHOULD NOT UPDATE IF WE ARE CALCULATING HOW FAR WE NEED TO GO
//     // float theta_mid = theta + (delta_theta / 2.0f);
//     // CurrPos_X += delta_s * cos(theta_mid);
//     // CurrPos_Y += delta_s * sin(theta_mid);

//     return Steps, Angle
// }

void inverse_bicycle(float Target_X, float Target_Y) {
    // Compute change in position
    float delta_x = Target_X - CurrPos_X;
    float delta_y = Target_Y - CurrPos_Y;
    
    // Compute distance to move (Δs)
    float delta_s = sqrt(delta_x * delta_x + delta_y * delta_y);
    
    // Compute desired heading angle (φ)
    float phi = atan2(delta_y, delta_x);
    
    // Compute change in heading angle (Δθ)
    float delta_theta = phi - theta;
    
    // Normalize delta_theta to be within [-π, π]
    if (delta_theta > PI)
        delta_theta -= 2.0f * PI;
    else if (delta_theta < -PI)
        delta_theta += 2.0f * PI;
    
    // Compute curvature (κ)
    float curvature;
    if (delta_s != 0.0f)
        curvature = delta_theta / delta_s;
    else
        curvature = 0.0f; // No movement needed
    
    // Compute effective steering angle (δ_eff)
    float effective_delta = atan(curvature * WHEELBASE);
    
    // Adjust for understeer
    float delta = effective_delta / UNDERSTEER_COEFF;
    
    // Convert steering angle to degrees
    int Desire_Angle = rad_to_degree(delta);
    
    // Compute required wheel steps
    int Steps = (delta_s / wheel_circumference) * COUNTS_PER_REV;

    return Steps,Desired_Angle;
}



