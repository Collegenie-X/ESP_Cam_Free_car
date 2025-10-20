#ifndef MOTOR_COMMAND_H
#define MOTOR_COMMAND_H

#include <Arduino.h>

/**
 * 모터 명령 타입 열거형
 */
enum CommandType {
    LEFT,       // 왼쪽으로 회전
    RIGHT,      // 오른쪽으로 회전
    CENTER,     // 중앙 (직진)
    STOP,       // 정지
    UNKNOWN     // 알 수 없는 명령
};

/**
 * 문자열을 명령 타입으로 변환하는 함수
 * @param cmd 명령 문자열 (예: "left", "right", "center", "stop")
 * @return CommandType 명령 타입
 */
CommandType parseCommand(String cmd) {
    // 문자열을 소문자로 변환
    cmd.toLowerCase();
    cmd.trim();
    
    // Early return 패턴으로 명령 파싱
    if (cmd == "left") {
        return LEFT;
    }
    
    if (cmd == "right") {
        return RIGHT;
    }
    
    if (cmd == "center") {
        return CENTER;
    }
    
    if (cmd == "stop") {
        return STOP;
    }
    
    // 알 수 없는 명령
    Serial.printf("알 수 없는 명령: %s\n", cmd.c_str());
    return UNKNOWN;
}

/**
 * 명령 타입을 문자열로 변환하는 함수
 * @param cmd 명령 타입
 * @return String 명령 문자열
 */
String commandToString(CommandType cmd) {
    switch (cmd) {
        case LEFT:
            return "LEFT";
        case RIGHT:
            return "RIGHT";
        case CENTER:
            return "CENTER";
        case STOP:
            return "STOP";
        default:
            return "UNKNOWN";
    }
}

#endif // MOTOR_COMMAND_H

