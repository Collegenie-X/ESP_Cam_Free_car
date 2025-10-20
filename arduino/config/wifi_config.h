#ifndef WIFI_CONFIG_H
#define WIFI_CONFIG_H

#include <WiFi.h>

// WiFi 설정 상수
const char* WIFI_SSID = "Kim";                // WiFi 이름
const char* WIFI_PASSWORD = "12345678";       // WiFi 비밀번호
const int WIFI_CONNECT_TIMEOUT = 20000;       // WiFi 연결 타임아웃 (ms)

/**
 * WiFi 연결 초기화 함수
 * @return 연결 성공 시 true, 실패 시 false
 */
bool initWiFiConnection() {
    // WiFi 연결 시작
    Serial.println("WiFi 연결 시도...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    // 연결 대기 (타임아웃 처리)
    unsigned long startTime = millis();
    while (WiFi.status() != WL_CONNECTED) {
        if (millis() - startTime > WIFI_CONNECT_TIMEOUT) {
            Serial.println("WiFi 연결 타임아웃!");
            return false;
        }
        
        delay(500);
        Serial.print(".");
    }
    
    // 연결 성공
    Serial.println("");
    Serial.println("WiFi 연결 성공!");
    Serial.print("IP 주소: ");
    Serial.println(WiFi.localIP());
    
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

