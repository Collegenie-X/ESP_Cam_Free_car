#ifndef WIFI_CONFIG_H
#define WIFI_CONFIG_H

#include <WiFi.h>

// WiFi 설정 상수
const char* WIFI_SSID = "edu";                // WiFi 이름
const char* WIFI_PASSWORD = "12345678";       // WiFi 비밀번호
const int WIFI_CONNECT_TIMEOUT = 20000;       // WiFi 연결 타임아웃 (ms)

/**
 * WiFi 연결 초기화 함수
 * @return 연결 성공 시 true, 실패 시 false
 */
bool initWiFiConnection() {
    // ✅ WiFi 모드 설정 및 전원 관리 최적화
    WiFi.mode(WIFI_STA);  // Station 모드
    WiFi.setSleep(false);  // WiFi 절전 모드 비활성화 (안정성 향상)
    WiFi.setAutoReconnect(true);  // 자동 재연결 활성화
    
    // WiFi 연결 시작
    Serial.println("WiFi 연결 시도...");
    Serial.printf("SSID: %s\n", WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    // 연결 대기 (타임아웃 처리)
    unsigned long startTime = millis();
    int dotCount = 0;
    while (WiFi.status() != WL_CONNECTED) {
        if (millis() - startTime > WIFI_CONNECT_TIMEOUT) {
            Serial.println("\n❌ WiFi 연결 타임아웃!");
            return false;
        }
        
        delay(500);
        Serial.print(".");
        dotCount++;
        
        // ✅ 10초마다 연결 상태 표시
        if (dotCount % 20 == 0) {
            Serial.printf(" [%d%%]\n", (int)((millis() - startTime) * 100 / WIFI_CONNECT_TIMEOUT));
        }
    }
    
    // 연결 성공
    Serial.println("");
    Serial.println("✅ WiFi 연결 성공!");
    Serial.printf("📡 IP 주소: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("📶 신호 강도: %d dBm\n", WiFi.RSSI());
    Serial.printf("🔧 MAC 주소: %s\n", WiFi.macAddress().c_str());
    
    return true;
}

/**
 * WiFi 연결 상태 확인 함수
 * @return 연결되어 있으면 true, 아니면 false
 */
bool isWiFiConnected() {
    return WiFi.status() == WL_CONNECTED;
}

/**
 * WiFi 재연결 함수
 */
void reconnectWiFi() {
    if (!isWiFiConnected()) {
        Serial.println("WiFi 재연결 중...");
        WiFi.disconnect();
        delay(1000);
        initWiFiConnection();
    }
}

#endif // WIFI_CONFIG_H

