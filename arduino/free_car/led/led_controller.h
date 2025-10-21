#ifndef LED_CONTROLLER_H
#define LED_CONTROLLER_H

#include <Arduino.h>
#include "../config/pin_config.h"

// LED 상태 저장
bool ledState = false;

/**
 * LED 초기화 함수
 */
void initLED() {
    Serial.println("LED 핀 초기화 중...");
    
    // LED 핀을 출력 모드로 설정
    pinMode(LED_PIN, OUTPUT);
    
    // 초기 상태: LED 꺼짐
    digitalWrite(LED_PIN, LOW);
    ledState = false;
    
    Serial.println("LED 핀 초기화 완료!");
}

/**
 * LED 켜기 함수
 */
void turnOnLED() {
    digitalWrite(LED_PIN, HIGH);
    ledState = true;
    Serial.println("💡 LED 켜짐");
}

/**
 * LED 끄기 함수
 */
void turnOffLED() {
    digitalWrite(LED_PIN, LOW);
    ledState = false;
    Serial.println("💡 LED 꺼짐");
}

/**
 * LED 토글 함수 (켜짐 ↔ 꺼짐 전환)
 */
void toggleLED() {
    if (ledState) {
        turnOffLED();
    } else {
        turnOnLED();
    }
}

/**
 * LED 상태 설정 함수
 * @param state true(켜짐) 또는 false(꺼짐)
 */
void setLEDState(bool state) {
    if (state) {
        turnOnLED();
    } else {
        turnOffLED();
    }
}

/**
 * LED 현재 상태 반환 함수
 * @return true(켜짐) 또는 false(꺼짐)
 */
bool getLEDState() {
    return ledState;
}

/**
 * LED 깜빡임 함수 (n회)
 * @param count 깜빡임 횟수
 * @param delayMs 깜빡임 간격 (밀리초)
 */
void blinkLED(int count, int delayMs = 200) {
    bool originalState = ledState;
    
    for (int i = 0; i < count; i++) {
        turnOnLED();
        delay(delayMs);
        turnOffLED();
        delay(delayMs);
    }
    
    // 원래 상태로 복원
    setLEDState(originalState);
}

/**
 * LED PWM 제어 함수 (밝기 조절)
 * @param brightness 밝기 (0-255)
 */
void setLEDBrightness(int brightness) {
    // 밝기 값 제한
    if (brightness < 0) brightness = 0;
    if (brightness > 255) brightness = 255;
    
    analogWrite(LED_PIN, brightness);
    ledState = (brightness > 0);
    
    Serial.printf("💡 LED 밝기: %d/255\n", brightness);
}

#endif // LED_CONTROLLER_H

