/*
 * ============================================================================
 * 프로젝트: Free Car - 자율주행차
 * 설명: ESP32-CAM을 사용한 WiFi 기반 자율주행차 시스템
 * 기능:
 *   - WiFi 연결 및 HTTP 서버 구동
 *   - 카메라 영상 스트리밍 (/stream)
 *   - 원격 모터 제어 (/control?cmd=[left|right|center|stop])
 *   - 원격 LED 제어 (/led?state=[on|off|toggle])
 *   - 상태 확인 (/status)
 * 
 * 하드웨어:
 *   - ESP32-CAM 모듈
 *   - L298N 모터 드라이버
 *   - DC 모터 x2
 * 
 * 작성자: Free Car Project Team
 * 날짜: 2025-10-20
 * 버전: 1.0.0
 * ============================================================================
 */

// ==================== 헤더 파일 포함 ====================
#include <WiFi.h>
#include "esp_camera.h"
#include "esp_http_server.h"

// Config 모듈
#include "config/wifi_config.h"
#include "config/pin_config.h"

// Camera 모듈
#include "camera/camera_init.h"
#include "camera/camera_stream_handler.h"

// Motor 모듈
#include "motor/motor_command.h"
#include "motor/motor_controller.h"

// LED 모듈
#include "led/led_controller.h"

// Server 모듈
#include "server/command_receiver.h"
#include "server/http_server_handler.h"


// ==================== Setup 함수 ====================
/**
 * 시스템 초기화 함수
 * - 시리얼 통신 초기화
 * - WiFi 연결
 * - 카메라 초기화
 * - 모터 초기화
 * - LED 초기화
 * - HTTP 서버 시작
 */
void setup() {
    // 1. 시리얼 통신 초기화
    Serial.begin(115200);
    Serial.println("");
    Serial.println("============================================");
    Serial.println("  Free Car - 자율주행차 시스템 시작");
    Serial.println("============================================");
    delay(1000);
    
    // 2. WiFi 연결
    Serial.println("\n[단계 1] WiFi 연결");
    if (!initWiFiConnection()) {
        Serial.println("❌ WiFi 연결 실패! 시스템을 재시작해주세요.");
        return;
    }
    Serial.println("✅ WiFi 연결 완료");
    
    // 3. 카메라 초기화
    Serial.println("\n[단계 2] 카메라 초기화");
    if (!initCamera()) {
        Serial.println("❌ 카메라 초기화 실패! 시스템을 재시작해주세요.");
        return;
    }
    Serial.println("✅ 카메라 초기화 완료");
    
    // 4. 모터 초기화
    Serial.println("\n[단계 3] 모터 초기화");
    initMotor();
    Serial.println("✅ 모터 초기화 완료");
    
    // 5. LED 초기화
    Serial.println("\n[단계 4] LED 초기화");
    initLED();
    Serial.println("✅ LED 초기화 완료");
    
    // 6. HTTP 서버 시작
    Serial.println("\n[단계 5] HTTP 서버 시작");
    if (!startHttpServer()) {
        Serial.println("❌ HTTP 서버 시작 실패! 시스템을 재시작해주세요.");
        return;
    }
    Serial.println("✅ HTTP 서버 시작 완료");
    
    // 7. 시스템 준비 완료
    Serial.println("\n============================================");
    Serial.println("  🚗 시스템 준비 완료!");
    Serial.println("============================================");
    Serial.printf("📡 웹 인터페이스: http://%s\n", WiFi.localIP().toString().c_str());
    Serial.printf("📹 스트리밍: http://%s/stream\n", WiFi.localIP().toString().c_str());
    Serial.printf("🎮 모터 제어: http://%s/control?cmd=[left|right|center|stop]\n", WiFi.localIP().toString().c_str());
    Serial.printf("💡 LED 제어: http://%s/led?state=[on|off|toggle]\n", WiFi.localIP().toString().c_str());
    Serial.printf("📊 상태: http://%s/status\n", WiFi.localIP().toString().c_str());
    Serial.println("============================================\n");
}


// ==================== Loop 함수 ====================
/**
 * 메인 루프 함수
 * - WiFi 연결 상태 모니터링
 * - HTTP 서버는 백그라운드에서 자동 실행
 */
void loop() {
    // WiFi 연결 상태 확인 (10초마다)
    static unsigned long lastCheckTime = 0;
    const unsigned long CHECK_INTERVAL = 10000;  // 10초
    
    if (millis() - lastCheckTime > CHECK_INTERVAL) {
        lastCheckTime = millis();
        
        // WiFi 연결 상태 확인
        if (!isWiFiConnected()) {
            Serial.println("⚠️  WiFi 연결이 끊어졌습니다. 재연결 시도...");
            reconnectWiFi();
        }
    }
    
    // HTTP 서버는 자동으로 요청을 처리하므로 별도 처리 불필요
    // 필요시 추가 기능 구현 가능
    
    delay(100);  // CPU 부하 감소
}


// ==================== 추가 유틸리티 함수 (선택사항) ====================

/**
 * 시스템 리셋 함수 (필요시 사용)
 */
void systemReset() {
    Serial.println("시스템을 재시작합니다...");
    stopMotor();
    stopHttpServer();
    delay(1000);
    ESP.restart();
}

/**
 * 디버그 정보 출력 함수 (필요시 사용)
 */
void printDebugInfo() {
    Serial.println("\n========== 디버그 정보 ==========");
    Serial.printf("WiFi SSID: %s\n", WIFI_SSID);
    Serial.printf("IP 주소: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("신호 강도: %d dBm\n", WiFi.RSSI());
    Serial.printf("HTTP 서버 상태: %s\n", isServerRunning() ? "실행 중" : "정지");
    Serial.printf("현재 명령: %s\n", commandToString(getCurrentCommand()).c_str());
    Serial.printf("LED 상태: %s\n", getLEDState() ? "켜짐" : "꺼짐");
    Serial.printf("자유 힙 메모리: %d bytes\n", ESP.getFreeHeap());
    Serial.println("================================\n");
}
