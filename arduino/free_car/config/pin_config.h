#ifndef PIN_CONFIG_H
#define PIN_CONFIG_H

// ==================== 모터 핀 설정 ====================
// 왼쪽 모터 (Motor A)
const int MOTOR_LEFT_FORWARD_PIN = 12;      // GPIO 12: 왼쪽 모터 전진
const int MOTOR_LEFT_BACKWARD_PIN = 13;     // GPIO 13: 왼쪽 모터 후진

// 오른쪽 모터 (Motor B)
const int MOTOR_RIGHT_FORWARD_PIN = 14;     // GPIO 14: 오른쪽 모터 전진
const int MOTOR_RIGHT_BACKWARD_PIN = 15;    // GPIO 15: 오른쪽 모터 후진

// ==================== 카메라 핀 설정 (ESP32-CAM) ====================
// ESP32-CAM의 기본 카메라 핀 설정 (OV2640)
const int CAMERA_PIN_PWDN = 32;             // Power Down 핀
const int CAMERA_PIN_RESET = -1;            // Reset 핀 (사용 안 함)
const int CAMERA_PIN_XCLK = 0;              // External Clock
const int CAMERA_PIN_SIOD = 26;             // I2C SDA
const int CAMERA_PIN_SIOC = 27;             // I2C SCL

const int CAMERA_PIN_D7 = 35;
const int CAMERA_PIN_D6 = 34;
const int CAMERA_PIN_D5 = 39;
const int CAMERA_PIN_D4 = 36;
const int CAMERA_PIN_D3 = 21;
const int CAMERA_PIN_D2 = 19;
const int CAMERA_PIN_D1 = 18;
const int CAMERA_PIN_D0 = 5;
const int CAMERA_PIN_VSYNC = 25;
const int CAMERA_PIN_HREF = 23;
const int CAMERA_PIN_PCLK = 22;

// ==================== 기타 설정 ====================
const int LED_PIN = 4;                      // LED 핀 (ESP32-CAM 내장 LED)

#endif // PIN_CONFIG_H

