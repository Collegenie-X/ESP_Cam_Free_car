#ifndef MOTOR_CONTROLLER_H
#define MOTOR_CONTROLLER_H

#include <Arduino.h>
#include "../config/pin_config.h"
#include "motor_command.h"

// ==================== 모터 속도 설정 (0-255) ====================
const int MOTOR_SPEED_MAX = 255;       // 최대 속도
const int MOTOR_SPEED_FAST = 230;      // 빠른 속도
const int MOTOR_SPEED_NORMAL = 200;    // 보통 속도
const int MOTOR_SPEED_SLOW = 150;      // 느린 속도
const int MOTOR_SPEED_TURN = 180;      // 회전 속도
const int MOTOR_SPEED_STOP = 0;        // 정지

// 현재 명령 상태 및 속도 저장
CommandType currentCommand = STOP;
int currentSpeed = MOTOR_SPEED_NORMAL;

/**
 * 모터 핀 초기화 함수
 */
void initMotor() {
    Serial.println("모터 핀 초기화 중...");
    
    // 모터 핀을 출력 모드로 설정
    pinMode(MOTOR_LEFT_FORWARD_PIN, OUTPUT);
    pinMode(MOTOR_LEFT_BACKWARD_PIN, OUTPUT);
    pinMode(MOTOR_RIGHT_FORWARD_PIN, OUTPUT);
    pinMode(MOTOR_RIGHT_BACKWARD_PIN, OUTPUT);
    
    // 초기 상태: 모든 핀 0 (정지)
    analogWrite(MOTOR_LEFT_FORWARD_PIN, 0);
    analogWrite(MOTOR_LEFT_BACKWARD_PIN, 0);
    analogWrite(MOTOR_RIGHT_FORWARD_PIN, 0);
    analogWrite(MOTOR_RIGHT_BACKWARD_PIN, 0);
    
    Serial.println("모터 핀 초기화 완료!");
    Serial.printf("  - 기본 속도: %d/255\n", MOTOR_SPEED_NORMAL);
}

/**
 * 모터 정지 함수
 */
void stopMotor() {
    analogWrite(MOTOR_LEFT_FORWARD_PIN, 0);
    analogWrite(MOTOR_LEFT_BACKWARD_PIN, 0);
    analogWrite(MOTOR_RIGHT_FORWARD_PIN, 0);
    analogWrite(MOTOR_RIGHT_BACKWARD_PIN, 0);
    
    currentCommand = STOP;
    Serial.println("🛑 모터 정지");
}

/**
 * 전진 함수 (속도 지정)
 * @param speed 모터 속도 (0-255)
 */
void moveForwardWithSpeed(int speed) {
    // 속도 값 제한
    if (speed < 0) speed = 0;
    if (speed > 255) speed = 255;
    
    // 양쪽 모터 전진
    analogWrite(MOTOR_LEFT_FORWARD_PIN, speed);
    analogWrite(MOTOR_LEFT_BACKWARD_PIN, 0);
    analogWrite(MOTOR_RIGHT_FORWARD_PIN, speed);
    analogWrite(MOTOR_RIGHT_BACKWARD_PIN, 0);
    
    currentCommand = CENTER;
    currentSpeed = speed;
    Serial.printf("⬆️  전진 (속도: %d/255)\n", speed);
}

/**
 * 전진 함수 (기본 속도)
 */
void moveForward() {
    moveForwardWithSpeed(currentSpeed);
}

/**
 * 후진 함수 (속도 지정)
 * @param speed 모터 속도 (0-255)
 */
void moveBackwardWithSpeed(int speed) {
    // 속도 값 제한
    if (speed < 0) speed = 0;
    if (speed > 255) speed = 255;
    
    // 양쪽 모터 후진
    analogWrite(MOTOR_LEFT_FORWARD_PIN, 0);
    analogWrite(MOTOR_LEFT_BACKWARD_PIN, speed);
    analogWrite(MOTOR_RIGHT_FORWARD_PIN, 0);
    analogWrite(MOTOR_RIGHT_BACKWARD_PIN, speed);
    
    currentSpeed = speed;
    Serial.printf("⬇️  후진 (속도: %d/255)\n", speed);
}

/**
 * 후진 함수 (기본 속도)
 */
void moveBackward() {
    moveBackwardWithSpeed(currentSpeed);
}

/**
 * 좌회전 함수 (속도 지정)
 * @param speed 회전 속도 (0-255)
 */
void turnLeftWithSpeed(int speed) {
    // 속도 값 제한
    if (speed < 0) speed = 0;
    if (speed > 255) speed = 255;
    
    // 왼쪽 모터 정지, 오른쪽 모터 전진
    analogWrite(MOTOR_LEFT_FORWARD_PIN, 0);
    analogWrite(MOTOR_LEFT_BACKWARD_PIN, 0);
    analogWrite(MOTOR_RIGHT_FORWARD_PIN, speed);
    analogWrite(MOTOR_RIGHT_BACKWARD_PIN, 0);
    
    currentCommand = LEFT;
    currentSpeed = speed;
    Serial.printf("⬅️  좌회전 (속도: %d/255)\n", speed);
}

/**
 * 좌회전 함수 (기본 속도)
 * 왼쪽 모터 정지, 오른쪽 모터 전진
 */
void turnLeft() {
    turnLeftWithSpeed(MOTOR_SPEED_TURN);
}

/**
 * 우회전 함수 (속도 지정)
 * @param speed 회전 속도 (0-255)
 */
void turnRightWithSpeed(int speed) {
    // 속도 값 제한
    if (speed < 0) speed = 0;
    if (speed > 255) speed = 255;
    
    // 왼쪽 모터 전진, 오른쪽 모터 정지
    analogWrite(MOTOR_LEFT_FORWARD_PIN, speed);
    analogWrite(MOTOR_LEFT_BACKWARD_PIN, 0);
    analogWrite(MOTOR_RIGHT_FORWARD_PIN, 0);
    analogWrite(MOTOR_RIGHT_BACKWARD_PIN, 0);
    
    currentCommand = RIGHT;
    currentSpeed = speed;
    Serial.printf("➡️  우회전 (속도: %d/255)\n", speed);
}

/**
 * 우회전 함수 (기본 속도)
 * 왼쪽 모터 전진, 오른쪽 모터 정지
 */
void turnRight() {
    turnRightWithSpeed(MOTOR_SPEED_TURN);
}

/**
 * 제자리 좌회전 (속도 지정)
 * @param speed 회전 속도 (0-255)
 */
void spinLeftWithSpeed(int speed) {
    // 속도 값 제한
    if (speed < 0) speed = 0;
    if (speed > 255) speed = 255;
    
    // 왼쪽 모터 후진, 오른쪽 모터 전진
    analogWrite(MOTOR_LEFT_FORWARD_PIN, 0);
    analogWrite(MOTOR_LEFT_BACKWARD_PIN, speed);
    analogWrite(MOTOR_RIGHT_FORWARD_PIN, speed);
    analogWrite(MOTOR_RIGHT_BACKWARD_PIN, 0);
    
    currentSpeed = speed;
    Serial.printf("↺ 제자리 좌회전 (속도: %d/255)\n", speed);
}

/**
 * 제자리 좌회전 (왼쪽 후진, 오른쪽 전진) - 기본 속도
 */
void spinLeft() {
    spinLeftWithSpeed(MOTOR_SPEED_TURN);
}

/**
 * 제자리 우회전 (속도 지정)
 * @param speed 회전 속도 (0-255)
 */
void spinRightWithSpeed(int speed) {
    // 속도 값 제한
    if (speed < 0) speed = 0;
    if (speed > 255) speed = 255;
    
    // 왼쪽 모터 전진, 오른쪽 모터 후진
    analogWrite(MOTOR_LEFT_FORWARD_PIN, speed);
    analogWrite(MOTOR_LEFT_BACKWARD_PIN, 0);
    analogWrite(MOTOR_RIGHT_FORWARD_PIN, 0);
    analogWrite(MOTOR_RIGHT_BACKWARD_PIN, speed);
    
    currentSpeed = speed;
    Serial.printf("↻ 제자리 우회전 (속도: %d/255)\n", speed);
}

/**
 * 제자리 우회전 (왼쪽 전진, 오른쪽 후진) - 기본 속도
 */
void spinRight() {
    spinRightWithSpeed(MOTOR_SPEED_TURN);
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

/**
 * 모터 속도 설정 함수
 * @param speed 새로운 기본 속도 (0-255)
 */
void setMotorSpeed(int speed) {
    // 속도 값 제한
    if (speed < 0) speed = 0;
    if (speed > 255) speed = 255;
    
    currentSpeed = speed;
    Serial.printf("⚙️  모터 기본 속도 설정: %d/255\n", speed);
}

/**
 * 현재 모터 속도 반환 함수
 * @return int 현재 속도 (0-255)
 */
int getMotorSpeed() {
    return currentSpeed;
}

/**
 * 모터 속도 증가 함수
 * @param step 증가량 (기본 10)
 * @return 증가 후 속도
 */
int increaseMotorSpeed(int step = 10) {
    if (step < 0) step = 0; // early guard
    int newSpeed = currentSpeed + step;
    if (newSpeed > MOTOR_SPEED_MAX) newSpeed = MOTOR_SPEED_MAX;
    setMotorSpeed(newSpeed);
    // 현재 동작이 전진/회전 등인 경우 즉시 반영
    switch (currentCommand) {
        case CENTER: moveForwardWithSpeed(newSpeed); break;
        case LEFT:   turnLeftWithSpeed(newSpeed); break;
        case RIGHT:  turnRightWithSpeed(newSpeed); break;
        default: break; // STOP 등은 속도만 업데이트
    }
    return currentSpeed;
}

/**
 * 모터 속도 감소 함수
 * @param step 감소량 (기본 10)
 * @return 감소 후 속도
 */
int decreaseMotorSpeed(int step = 10) {
    if (step < 0) step = 0; // early guard
    int newSpeed = currentSpeed - step;
    if (newSpeed < 0) newSpeed = 0;
    setMotorSpeed(newSpeed);
    switch (currentCommand) {
        case CENTER: moveForwardWithSpeed(newSpeed); break;
        case LEFT:   turnLeftWithSpeed(newSpeed); break;
        case RIGHT:  turnRightWithSpeed(newSpeed); break;
        default: break;
    }
    return currentSpeed;
}

/**
 * 모터 동작 여부 반환 함수
 * @return true(동작 중) / false(정지)
 */
bool isMotorRunning() {
    return currentCommand != STOP && currentSpeed > 0;
}

/**
 * 개별 모터 제어 함수 (고급 기능)
 * @param leftSpeed 왼쪽 모터 속도 (-255 ~ 255, 음수는 후진)
 * @param rightSpeed 오른쪽 모터 속도 (-255 ~ 255, 음수는 후진)
 */
void setMotorIndividual(int leftSpeed, int rightSpeed) {
    // 왼쪽 모터 제어
    if (leftSpeed > 0) {
        // 전진
        leftSpeed = constrain(leftSpeed, 0, 255);
        analogWrite(MOTOR_LEFT_FORWARD_PIN, leftSpeed);
        analogWrite(MOTOR_LEFT_BACKWARD_PIN, 0);
    } else if (leftSpeed < 0) {
        // 후진
        leftSpeed = constrain(-leftSpeed, 0, 255);
        analogWrite(MOTOR_LEFT_FORWARD_PIN, 0);
        analogWrite(MOTOR_LEFT_BACKWARD_PIN, leftSpeed);
    } else {
        // 정지
        analogWrite(MOTOR_LEFT_FORWARD_PIN, 0);
        analogWrite(MOTOR_LEFT_BACKWARD_PIN, 0);
    }
    
    // 오른쪽 모터 제어
    if (rightSpeed > 0) {
        // 전진
        rightSpeed = constrain(rightSpeed, 0, 255);
        analogWrite(MOTOR_RIGHT_FORWARD_PIN, rightSpeed);
        analogWrite(MOTOR_RIGHT_BACKWARD_PIN, 0);
    } else if (rightSpeed < 0) {
        // 후진
        rightSpeed = constrain(-rightSpeed, 0, 255);
        analogWrite(MOTOR_RIGHT_FORWARD_PIN, 0);
        analogWrite(MOTOR_RIGHT_BACKWARD_PIN, rightSpeed);
    } else {
        // 정지
        analogWrite(MOTOR_RIGHT_FORWARD_PIN, 0);
        analogWrite(MOTOR_RIGHT_BACKWARD_PIN, 0);
    }
    
    Serial.printf("🎮 개별 모터 제어 - 왼쪽: %d, 오른쪽: %d\n", leftSpeed, rightSpeed);
}

#endif // MOTOR_CONTROLLER_H

