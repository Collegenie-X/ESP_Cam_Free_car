//www.kuongshun.com

//    The direction of the car's movement
//  ENA   ENB   gpLb  gpLf  gpRb  gpRf   Description  
//  HIGH  HIGH  LOW   HIGH  LOW   HIGH  Car is runing forward
//  HIGH  HIGH  HIGH  LOW   HIGH  LOW   Car is runing back
//  HIGH  HIGH  HIGH  LOW   LOW   HIGH  Car is turning left
//  HIGH  HIGH  LOW   HIGH  HIGH  LOW   Car is turning right
//  HIGH  HIGH  LOW   LOW   LOW   LOW   Car is stoped
//  HIGH  HIGH  HIGH  HIGH  HIGH  HIGH  Car is stoped
//  LOW   LOW   N/A   N/A   N/A   N/A   Car is stoped


//define L298n module IO Pin
#define ENA 2   // Left
#define ENB 12    // Right
#define gpRb 14  // left Backward
#define gpRf 13  // left Forward
#define gpLb 33  // Right Backward
#define gpLf 15  // right Forward

void forward(){ 
  digitalWrite(ENA,HIGH); //enable L298n A channel
  digitalWrite(ENB,HIGH); //enable L298n B channel
  digitalWrite(gpLb,LOW); //set gpLb low level
  digitalWrite(gpLf,HIGH);  //set gpLf hight level
  digitalWrite(gpRb,LOW);  //set gpRb low level
  digitalWrite(gpRf,HIGH); //set gpRf hight level
  Serial.println("Forward");//send message to serial monitor
}

void back(){
  digitalWrite(ENA,HIGH);  //enable L298n A channel
  digitalWrite(ENB,HIGH);  //enable L298n B channel
  digitalWrite(gpLb,HIGH); //set gpLb hight level
  digitalWrite(gpLf,LOW);   //set gpLf low level
  digitalWrite(gpRb,HIGH);  //set gpRb hight level
  digitalWrite(gpRf,LOW);   //set gpRf low level
  Serial.println("Back");   //send message to serial monitor
} 

void left(){
  digitalWrite(ENA,HIGH);  //enable L298n A channel
  digitalWrite(ENB,HIGH);  //enable L298n B channel
  digitalWrite(gpLb,HIGH); //set gpLb hight level
  digitalWrite(gpLf,LOW); //set gpLf low level
  digitalWrite(gpRb,LOW); //set gpRb low level
  digitalWrite(gpRf,HIGH); //set gpRf hight level
  Serial.println("Left"); //send message to serial monitor
} 

void right(){
  digitalWrite(ENA,HIGH); //enable L298n A channel
  digitalWrite(ENB,HIGH); //enable L298n B channel
  digitalWrite(gpLb,LOW); //set gpLb low level
  digitalWrite(gpLf,HIGH); //set gpLf hight level
  digitalWrite(gpRb,HIGH); //set gpRb hight level
  digitalWrite(gpRf,LOW); //set gpRf low level
  Serial.println("Right"); //send message to serial monitor
}

//before execute loop() function, 
//setup() function will execute first and only execute once
void setup() {
  Serial.begin(9600);//open serial and set the baudrate
  pinMode(gpLb,OUTPUT);//before useing io pin, pin mode must be set first 
  pinMode(gpLf,OUTPUT);
  pinMode(gpRb,OUTPUT);
  pinMode(gpRf,OUTPUT);
  pinMode(ENA,OUTPUT);
  pinMode(ENB,OUTPUT);
}

//Repeat execution
void loop() {
  forward();  //go forward
  delay(1000);//delay 1000 ms
  back();     //go back
  delay(1000);
  left();     //turning left
  delay(1000);
  right();    //turning right
  delay(1000);
}
