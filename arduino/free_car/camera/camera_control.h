#ifndef CAMERA_CONTROL_H
#define CAMERA_CONTROL_H

#include "esp_camera.h"
#include <Arduino.h>

/**
 * 카메라 센서 설정 실시간 제어 모듈
 * GET 방식으로 밝기, 대비, 게인 등을 동적 조정
 */

/**
 * 밝기 설정 함수
 * @param value -2 ~ 2 범위
 * @return 설정 성공 여부
 */
bool setCameraBrightness(int value) {
    sensor_t* sensor = esp_camera_sensor_get();
    if (!sensor) {
        Serial.println("카메라 센서를 가져올 수 없습니다!");
        return false;
    }
    
    // 범위 제한
    if (value < -2) value = -2;
    if (value > 2) value = 2;
    
    int result = sensor->set_brightness(sensor, value);
    Serial.printf("🔆 밝기 설정: %d (결과: %s)\n", value, result == 0 ? "성공" : "실패");
    return result == 0;
}

/**
 * 대비 설정 함수
 * @param value -2 ~ 2 범위
 * @return 설정 성공 여부
 */
bool setCameraContrast(int value) {
    sensor_t* sensor = esp_camera_sensor_get();
    if (!sensor) return false;
    
    if (value < -2) value = -2;
    if (value > 2) value = 2;
    
    int result = sensor->set_contrast(sensor, value);
    Serial.printf("🔆 대비 설정: %d (결과: %s)\n", value, result == 0 ? "성공" : "실패");
    return result == 0;
}

/**
 * 채도 설정 함수
 * @param value -2 ~ 2 범위
 * @return 설정 성공 여부
 */
bool setCameraSaturation(int value) {
    sensor_t* sensor = esp_camera_sensor_get();
    if (!sensor) return false;
    
    if (value < -2) value = -2;
    if (value > 2) value = 2;
    
    int result = sensor->set_saturation(sensor, value);
    Serial.printf("🔆 채도 설정: %d (결과: %s)\n", value, result == 0 ? "성공" : "실패");
    return result == 0;
}

/**
 * AGC 게인 설정 함수
 * @param value 0 ~ 30 범위
 * @return 설정 성공 여부
 */
bool setCameraAgcGain(int value) {
    sensor_t* sensor = esp_camera_sensor_get();
    if (!sensor) return false;
    
    if (value < 0) value = 0;
    if (value > 30) value = 30;
    
    int result = sensor->set_agc_gain(sensor, value);
    Serial.printf("🔆 AGC 게인 설정: %d (결과: %s)\n", value, result == 0 ? "성공" : "실패");
    return result == 0;
}

/**
 * 게인 상한 설정 함수
 * @param value 0 ~ 6 범위 (gainceiling_t)
 * @return 설정 성공 여부
 */
bool setCameraGainCeiling(int value) {
    sensor_t* sensor = esp_camera_sensor_get();
    if (!sensor) return false;
    
    if (value < 0) value = 0;
    if (value > 6) value = 6;
    
    int result = sensor->set_gainceiling(sensor, (gainceiling_t)value);
    Serial.printf("🔆 게인 상한 설정: %d (결과: %s)\n", value, result == 0 ? "성공" : "실패");
    return result == 0;
}

/**
 * AEC2 설정 함수 (자동 노출 제어)
 * @param value 0 (비활성화) 또는 1 (활성화)
 * @return 설정 성공 여부
 */
bool setCameraAec2(int value) {
    sensor_t* sensor = esp_camera_sensor_get();
    if (!sensor) return false;
    
    value = (value != 0) ? 1 : 0;
    
    int result = sensor->set_aec2(sensor, value);
    Serial.printf("🔆 AEC2 설정: %d (결과: %s)\n", value, result == 0 ? "성공" : "실패");
    return result == 0;
}

/**
 * 수평 미러 설정 함수
 * @param value 0 (비활성화) 또는 1 (활성화)
 * @return 설정 성공 여부
 */
bool setCameraHmirror(int value) {
    sensor_t* sensor = esp_camera_sensor_get();
    if (!sensor) return false;
    
    value = (value != 0) ? 1 : 0;
    
    int result = sensor->set_hmirror(sensor, value);
    Serial.printf("🔆 수평 미러 설정: %d (결과: %s)\n", value, result == 0 ? "성공" : "실패");
    return result == 0;
}

/**
 * 수직 플립 설정 함수
 * @param value 0 (비활성화) 또는 1 (활성화)
 * @return 설정 성공 여부
 */
bool setCameraVflip(int value) {
    sensor_t* sensor = esp_camera_sensor_get();
    if (!sensor) return false;
    
    value = (value != 0) ? 1 : 0;
    
    int result = sensor->set_vflip(sensor, value);
    Serial.printf("🔆 수직 플립 설정: %d (결과: %s)\n", value, result == 0 ? "성공" : "실패");
    return result == 0;
}

/**
 * 현재 카메라 센서 설정값 조회 함수
 * @return JSON 형식 문자열
 */
String getCameraSettings() {
    sensor_t* sensor = esp_camera_sensor_get();
    if (!sensor) {
        return "{\"error\": \"sensor not available\"}";
    }
    
    String json = "{\n";
    json += "  \"brightness\": " + String(sensor->status.brightness) + ",\n";
    json += "  \"contrast\": " + String(sensor->status.contrast) + ",\n";
    json += "  \"saturation\": " + String(sensor->status.saturation) + ",\n";
    json += "  \"agc_gain\": " + String(sensor->status.agc_gain) + ",\n";
    json += "  \"gainceiling\": " + String(sensor->status.gainceiling) + ",\n";
    json += "  \"aec2\": " + String(sensor->status.aec2) + ",\n";
    json += "  \"hmirror\": " + String(sensor->status.hmirror) + ",\n";
    json += "  \"vflip\": " + String(sensor->status.vflip) + "\n";
    json += "}";
    
    return json;
}

#endif // CAMERA_CONTROL_H

