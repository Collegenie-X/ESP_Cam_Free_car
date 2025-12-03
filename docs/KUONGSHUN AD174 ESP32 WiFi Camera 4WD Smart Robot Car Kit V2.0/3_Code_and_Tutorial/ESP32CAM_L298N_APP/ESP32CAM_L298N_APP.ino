#include <WiFi.h>
#include "esp_camera.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

WiFiServer server(100);

byte Stop[17]={0xff,0x55,0x0a,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0x0C,0x00,0x00};
char buffer[52];
byte RX_package[17] = {0};
byte dataLen, index_a = 0;
unsigned char prevc=0;
int dataIndex = 0;
int LED_mode=0,LED_val=0;
int speed=225;
String sendBuff;
String Version = "Firmware Version is 0.12.21";
bool ED_client = true;
bool WA_en = false;
bool isStart = false;

#define gpLED  4      // Light

void CameraWebServer_init();
extern int gpLb = 14; // Left 1
extern int gpLf = 13; // Left 2
extern int gpRb = 33; // Right 1
extern int gpRf = 15; // Right 2
extern int gpLed = 4; // Light
extern int ENR = 2;
extern int ENL = 12;

bool st = false;
unsigned long lastDataTimes = 0;

void initMotors()
{
  pinMode(gpLb, OUTPUT); //Left Backward
  pinMode(gpLf, OUTPUT); //Left Forward
  pinMode(gpRb, OUTPUT); //Right Forward
  pinMode(gpRf, OUTPUT); //Right Backward
  pinMode(gpLed, OUTPUT); //Light
  pinMode(ENR, OUTPUT);
  pinMode(ENL, OUTPUT);

  ledcSetup(2,5000,8);
  ledcSetup(12,5000,8);
  ledcAttachPin(ENR,2);
  ledcAttachPin(ENL,12);
  ledcWrite(ENR, 0);
  ledcWrite(ENL, 0);
  digitalWrite(gpLf, LOW);
  digitalWrite(gpRb, LOW);
  digitalWrite(gpRf, LOW);
}

unsigned char readBuffer(int index_r)
{
  return buffer[index_r]; 
}
void writeBuffer(int index_w,unsigned char c)
{
  buffer[index_w]=c;
}

void setup()
{
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); // prevent brownouts by silencing them
  Serial.begin(115200);
  Serial.setDebugOutput(true);

  //http://192.168.4.1/control?var=framesize&val=3
  //http://192.168.4.1/Test?var=
  CameraWebServer_init();
  server.begin();
  delay(100);

  // Remote Control Car
  initMotors();
  ledcSetup(7, 5000, 8);
  ledcAttachPin(gpLed, 7);  //pin4 is LED
  for (int i = 0; i < 5; i++) 
  {
    ledcWrite(7, 20); // flash led
    delay(50);
    ledcWrite(7, 0);
    delay(50);
  }
}

void loop() {
/*
        if (RX_package[0] == 0xff && RX_package[1] == 0x55) {
        LED_mode = RX_package[10];
        LED_val = RX_package[12];
        Serial.println("LED_val");
        Serial.println(LED_val);
        if (LED_mode == 0x05) {
          if (LED_val < 50) LED_val = 0;
          ledcWrite(7, LED_val);
          delay(1);
        }
        }
 */
 RXpack_func();
}

void parseData()
{ 
    isStart = false;
    //int action = readBuffer(9);
    int device = readBuffer(10);
    int val = readBuffer(12);
    switch(device) 
  {
    case 0x0C:
    {   
      switch (val)
      {
        case 0x01:
            WheelAct(speed, speed, HIGH, LOW, HIGH, LOW);
            break;
        case 0x02:
            WheelAct(speed, speed, LOW, HIGH, LOW, HIGH);
            break;
        case 0x03:
            WheelAct(speed, speed, HIGH, LOW, LOW, HIGH);
            break;
        case 0x04:
            WheelAct(speed, speed, LOW, HIGH, HIGH, LOW);
            break;
        case 0x00:
            WheelAct(0, 0, LOW, LOW, LOW, LOW);
            break;
        default:
            break;
      }
    }break;
    
    case 0x05:
    {    
      if (val < 50) val = 0;
      ledcWrite(7, val);
      delay(5);
    }break;
    case 0x0D:
    {
        speed = val;
    }break;
  }   
}


void RXpack_func()  //Receive data
{
  WiFiClient client = server.available();
  if (client)
  {
    WA_en = true;
    ED_client = true;
    unsigned long previousMillis = millis();  // 上一个检查时间
    const unsigned long timeoutDuration = 3000;  // 超时时间（2秒）
    Serial.println("[Client connected]");
    while (client.connected())
    {
     if ((millis() - previousMillis) > timeoutDuration && client.available() == 0 && st==true)
      {
        break;
      } 
      if (client.available())
      {
        previousMillis = millis();
        unsigned char c = client.read()&0xff;
        Serial.write(c);

        st = false;         // 111111
        if (c == 200)
        {
          st = true;
        }

        if(c==0x55&&isStart==false)
        {
          if(prevc==0xff)
          {
            index_a=1;
            isStart = true;
          }
        }
        else
        {
          prevc = c;
          if(isStart)
          {
            if(index_a==2)
            {
            dataLen = c; 
            }
            else if(index_a>2)
            {
              dataLen--;
            }
            writeBuffer(index_a,c);
          }
        }
        index_a++;
        if(index_a>120)
        {
          index_a=0; 
          isStart=false;
        }
        if(isStart&&dataLen==0&&index_a>3)
        { 
          isStart = false;
          parseData();
          index_a=0;
        }
      }
     else if ((millis() - previousMillis) > timeoutDuration && Serial.available() == 0 && st==true)
       {
        WheelAct(0, 0, LOW, LOW, LOW, LOW);
       }   

      //functionMode();
      if (Serial.available())
      {
        char c = Serial.read();
        sendBuff += c;
        client.print(sendBuff);
        Serial.print(sendBuff);
        sendBuff = "";
      }
      static unsigned long Test_time = 0;
      if (millis() - Test_time > 1000)
      {
        Test_time = millis();
        if (0 == (WiFi.softAPgetStationNum()))
        {
          Serial.write(Stop,17);
          break;
        }
      }
    }
    Serial.write(Stop,17);
    client.stop();
    Serial.println("[Client disconnected]");
  }
  else
  {
    if (ED_client == true)
    {
      ED_client = false;
      Serial.write(Stop,17);
      WheelAct(0, 0, LOW, LOW, LOW, LOW);
    }
  }
}

void WheelAct(int speed_R, int speed_L, int nLf, int nLb, int nRf, int nRb)
{
    ledcWrite(ENR, speed_R);
    ledcWrite(ENL, speed_L);
    digitalWrite(gpLf, nLf);
    digitalWrite(gpLb, nLb);
    digitalWrite(gpRf, nRf);
    digitalWrite(gpRb, nRb);
}
