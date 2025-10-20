#ifndef MOTOR_CONTROLLER_H
#define MOTOR_CONTROLLER_H

#include <Arduino.h>
#include "../config/pin_config.h"
#include "motor_command.h"

// 모터 속도 설정 (0-255)
const int MOTOR_SPEED_FAST = 255;      // 빠른 속도
const int MOTOR_SPEED_NORMAL = 200;    // 보통 속도
const int MOTOR_SPEED_SLOW = 150;      // 느린 속도
const int MOTOR_SPEED_STOP = 0;        // 정지

// 현재 명령 상태 저장
CommandType currentCommand = STOP;

/**
 * 모터 핀 초기화 함수
 */
void initMotor() {
    Serial.println("모터 핀 초기화 중...");
    
    // 왼쪽 모터 핀 설정
    pinMode(MOTOR_LEFT_FORWARD_PIN, OUTPUT);
    pinMode(MOTOR_LEFT_BACKWARD_PIN, OUTPUT);
    
    // 오른쪽 모터 핀 설정
    pinMode(MOTOR_RIGHT_FORWARD_PIN, OUTPUT);
    pinMode(MOTOR_RIGHT_BACKWARD_PIN, OUTPUT);
    
    // 초기 상태: 모든 핀 LOW (정지)
    digitalWrite(MOTOR_LEFT_FORWARD_PIN, LOW);
    digitalWrite(MOTOR_LEFT_BACKWARD_PIN, LOW);
    digitalWrite(MOTOR_RIGHT_FORWARD_PIN, LOW);
    digitalWrite(MOTOR_RIGHT_BACKWARD_PIN, LOW);
    
    Serial.println("모터 핀 초기화 완료!");
}

/**
 * 모터 정지 함수
 */
void stopMotor() {
    digitalWrite(MOTOR_LEFT_FORWARD_PIN, LOW);
    digitalWrite(MOTOR_LEFT_BACKWARD_PIN, LOW);
    digitalWrite(MOTOR_RIGHT_FORWARD_PIN, LOW);
    digitalWrite(MOTOR_RIGHT_BACKWARD_PIN, LOW);
    
    currentCommand = STOP;
    Serial.println("모터 정지");
}

/**
 * 전진 함수
 */
void moveForward() {
    // 양쪽 모터 전진
    digitalWrite(MOTOR_LEFT_FORWARD_PIN, HIGH);
    digitalWrite(MOTOR_LEFT_BACKWARD_PIN, LOW);
    digitalWrite(MOTOR_RIGHT_FORWARD_PIN, HIGH);
    digitalWrite(MOTOR_RIGHT_BACKWARD_PIN, LOW);
    
    currentCommand = CENTER;
    Serial.println("전진 (중앙)");
}

/**
 * 후진 함수
 */
void moveBackward() {
    // 양쪽 모터 후진
    digitalWrite(MOTOR_LEFT_FORWARD_PIN, LOW);
    digitalWrite(MOTOR_LEFT_BACKWARD_PIN, HIGH);
    digitalWrite(MOTOR_RIGHT_FORWARD_PIN, LOW);
    digitalWrite(MOTOR_RIGHT_BACKWARD_PIN, HIGH);
    
    Serial.println("후진");
}

/**
 * 좌회전 함수
 * 왼쪽 모터는 느리게, 오른쪽 모터는 빠르게
 */
void turnLeft() {
    // 왼쪽 모터 정지 또는 느리게, 오른쪽 모터 전진
    digitalWrite(MOTOR_LEFT_FORWARD_PIN, LOW);
    digitalWrite(MOTOR_LEFT_BACKWARD_PIN, LOW);
    digitalWrite(MOTOR_RIGHT_FORWARD_PIN, HIGH);
    digitalWrite(MOTOR_RIGHT_BACKWARD_PIN, LOW);
    
    currentCommand = LEFT;
    Serial.println("좌회전");
}

/**
 * 우회전 함수
 * 왼쪽 모터는 빠르게, 오른쪽 모터는 느리게
 */
void turnRight() {
    // 왼쪽 모터 전진, 오른쪽 모터 정지 또는 느리게
    digitalWrite(MOTOR_LEFT_FORWARD_PIN, HIGH);
    digitalWrite(MOTOR_LEFT_BACKWARD_PIN, LOW);
    digitalWrite(MOTOR_RIGHT_FORWARD_PIN, LOW);
    digitalWrite(MOTOR_RIGHT_BACKWARD_PIN, LOW);
    
    currentCommand = RIGHT;
    Serial.println("우회전");
}

/**
 * 제자리 좌회전 (왼쪽 후진, 오른쪽 전진)
 */
void spinLeft() {
    digitalWrite(MOTOR_LEFT_FORWARD_PIN, LOW);
    digitalWrite(MOTOR_LEFT_BACKWARD_PIN, HIGH);
    digitalWrite(MOTOR_RIGHT_FORWARD_PIN, HIGH);
    digitalWrite(MOTOR_RIGHT_BACKWARD_PIN, LOW);
    
    Serial.println("제자리 좌회전");
}

/**
 * 제자리 우회전 (왼쪽 전진, 오른쪽 후진)
 */
void spinRight() {
    digitalWrite(MOTOR_LEFT_FORWARD_PIN, HIGH);
    digitalWrite(MOTOR_LEFT_BACKWARD_PIN, LOW);
    digitalWrite(MOTOR_RIGHT_FORWARD_PIN, LOW);
    digitalWrite(MOTOR_RIGHT_BACKWARD_PIN, HIGH);
    
    Serial.println("제자리 우회전");
}

/**
 * 명령 실행 함수
 * @param cmd 실행할 명령 타입
 */
void executeCommand(CommandType cmd) {
    // Early return: 동일한 명령이면 실행하지 않음
    if (cmd == currentCommand) {
        return;
    }
    
    // 명령에 따라 모터 제어
    switch (cmd) {
        case LEFT:
            turnLeft();
            break;
            
        case RIGHT:
            turnRight();
            break;
            
        case CENTER:
            moveForward();
            break;
            
        case STOP:
            stopMotor();
            break;
            
        default:
            Serial.println("알 수 없는 명령입니다!");
            stopMotor();
            break;
    }
}

/**
 * 현재 명령 상태 반환 함수
 * @return CommandType 현재 명령 타입
 */
CommandType getCurrentCommand() {
    return currentCommand;
}

#endif // MOTOR_CONTROLLER_H

