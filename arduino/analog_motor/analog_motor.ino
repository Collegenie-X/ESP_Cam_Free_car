/*
  Project: adjust motor speed
  Author: Keyestudio
  Function: how to control the moving speed of the car
*/
//set motor control pins
#define MOTOR_R_PIN_1 14
#define MOTOR_R_PIN_2 15
#define MOTOR_L_PIN_1 13
#define MOTOR_L_PIN_2 12
//Define the initial value of the speed to be 100; if you want to change the speed of the car, just change the values of the two variables (range from 0 to 255).
int MOTOR_R_Speed = 70;
int MOTOR_L_Speed = 70;

void setup() {
  //set serial baud rate
  Serial.begin(115200);
  //set pin modes
  pinMode(MOTOR_R_PIN_1, OUTPUT);
  pinMode(MOTOR_R_PIN_2, OUTPUT);
  pinMode(MOTOR_L_PIN_1, OUTPUT);
  pinMode(MOTOR_L_PIN_2, OUTPUT);


  // Forward 
  analogWrite(MOTOR_R_PIN_2, MOTOR_R_Speed);
  analogWrite(MOTOR_L_PIN_1, MOTOR_L_Speed);
  analogWrite(MOTOR_L_PIN_2, 0);
  delay(1000);

  // Backward
  Serial.println("Backward");
  analogWrite(MOTOR_R_PIN_1, MOTOR_R_Speed);
  analogWrite(MOTOR_R_PIN_2, 0);
  analogWrite(MOTOR_L_PIN_1, 0);
  analogWrite(MOTOR_L_PIN_2, MOTOR_L_Speed);
  delay(1000);

  // Left
  Serial.println("Left");
  analogWrite(MOTOR_R_PIN_1, 0);
  analogWrite(MOTOR_R_PIN_2, MOTOR_R_Speed);
  analogWrite(MOTOR_L_PIN_1, 0);
  analogWrite(MOTOR_L_PIN_2, MOTOR_L_Speed);
  delay(1000);
  
  // Right
  Serial.println("Right");
  analogWrite(MOTOR_R_PIN_1, MOTOR_R_Speed);
  analogWrite(MOTOR_R_PIN_2, 0);
  analogWrite(MOTOR_L_PIN_1, MOTOR_L_Speed);
  analogWrite(MOTOR_L_PIN_2, 0);
  delay(1000);
  
  // Stop
  Serial.println("Stop");
  analogWrite(MOTOR_R_PIN_1, 0);
  analogWrite(MOTOR_R_PIN_2, 0);
  analogWrite(MOTOR_L_PIN_1, 0);
  analogWrite(MOTOR_L_PIN_2, 0);
  delay(1000);
}

void loop() {
  // put your main code here, to run repeatedly:
   //Forward .  Use analogWrite to output analog values for speed control
  
}  