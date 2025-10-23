#ifndef CAMERA_INIT_H
#define CAMERA_INIT_H

#include "esp_camera.h"
#include "../config/pin_config.h"

/**
 * 카메라 설정 구조체 반환 함수
 * @return camera_config_t 카메라 설정
 */
camera_config_t getCameraConfig() {
    camera_config_t config;
    
    // 카메라 핀 설정
    config.pin_pwdn = CAMERA_PIN_PWDN;
    config.pin_reset = CAMERA_PIN_RESET;
    config.pin_xclk = CAMERA_PIN_XCLK;
    config.pin_sscb_sda = CAMERA_PIN_SIOD;
    config.pin_sscb_scl = CAMERA_PIN_SIOC;
    
    config.pin_d7 = CAMERA_PIN_D7;
    config.pin_d6 = CAMERA_PIN_D6;
    config.pin_d5 = CAMERA_PIN_D5;
    config.pin_d4 = CAMERA_PIN_D4;
    config.pin_d3 = CAMERA_PIN_D3;
    config.pin_d2 = CAMERA_PIN_D2;
    config.pin_d1 = CAMERA_PIN_D1;
    config.pin_d0 = CAMERA_PIN_D0;
    config.pin_vsync = CAMERA_PIN_VSYNC;
    config.pin_href = CAMERA_PIN_HREF;
    config.pin_pclk = CAMERA_PIN_PCLK;
    
    // 카메라 설정 (캡처 속도 + 품질 균형)
    config.xclk_freq_hz = 20000000;           // ✅ XCLK 주파수 (20MHz - 안정적)
    config.ledc_timer = LEDC_TIMER_0;         // LEDC 타이머
    config.ledc_channel = LEDC_CHANNEL_0;     // LEDC 채널
    
    config.pixel_format = PIXFORMAT_JPEG;     // JPEG 포맷
    
    // ✅ 자율주행 최적화 (속도 + 품질 균형)
    if (psramFound()) {
        // PSRAM 있음: 품질 개선 버전
        config.frame_size = FRAMESIZE_QVGA;   // ✅ 320x240 (빠른 속도)
        config.jpeg_quality = 10;              // ✅ 품질 8 (선명한 이미지)
        config.fb_count = 1;                  // 단일 버퍼 (빠른 반환)
        Serial.println("✅ PSRAM 감지: 균형 모드 (QVGA 320x240, Q=10, 20MHz)");
    } else {
        // PSRAM 없음: 기본 품질
        config.frame_size = FRAMESIZE_QVGA;   // 320x240 (작은 해상도)
        config.jpeg_quality = 10;             // 품질 10 (적절한 균형)
        config.fb_count = 1;                  // 단일 버퍼
        Serial.println("✅ PSRAM 미감지: 균형 모드 (QVGA 320x240, Q=10, 20MHz)");
    }
    
    return config;
}

/**
 * 카메라 초기화 함수
 * @return 초기화 성공 시 true, 실패 시 false
 */
bool initCamera() {
    Serial.println("카메라 초기화 중...");
    
    // 카메라 설정 가져오기
    camera_config_t config = getCameraConfig();
    
    // 카메라 초기화
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("카메라 초기화 실패! 에러 코드: 0x%x\n", err);
        return false;
    }
    
    // 카메라 센서 설정
    sensor_t* sensor = esp_camera_sensor_get();
    if (sensor == NULL) {
        Serial.println("카메라 센서를 가져올 수 없습니다!");
        return false;
    }
    
    // ✅ 센서 설정 최적화 (품질 + 속도 균형)
    sensor->set_brightness(sensor, 2);        // 밝기: 1 (적당히 밝게)
    sensor->set_contrast(sensor, 2);          // 대비: 1 (차선 구분 향상)
    sensor->set_saturation(sensor, 2);        // 채도: 0 (자연스러운 색상)
    sensor->set_special_effect(sensor, 0);    // 특수 효과: 0 (없음)
    sensor->set_whitebal(sensor, 1);          // 화이트 밸런스: 1 (자동)
    sensor->set_awb_gain(sensor, 1);          // AWB 게인: 1 (활성화)
    sensor->set_wb_mode(sensor, 0);           // WB 모드: 0 (자동)
    sensor->set_exposure_ctrl(sensor, 1);     // 노출 제어: 1 (자동)
    sensor->set_aec2(sensor, 1);              // ✅ AEC2: 1 (활성화 - 품질 개선)
    sensor->set_ae_level(sensor, 1);          // ✅ AE 레벨: 1 (약간 밝게)
    sensor->set_aec_value(sensor, 1200);       // ✅ AEC 값: 400 (적절한 노출)
    sensor->set_gain_ctrl(sensor, 1);         // 게인 제어: 1 (자동)
    sensor->set_agc_gain(sensor, 30);          // ✅ AGC 게인: 8 (밝기 증가)
    sensor->set_gainceiling(sensor, (gainceiling_t)3);  // ✅ 게인 상한: 3 (품질 균형)
    sensor->set_bpc(sensor, 1);               // ✅ BPC: 1 (활성화 - 노이즈 제거)
    sensor->set_wpc(sensor, 0);               // WPC: 1 (활성화)
    sensor->set_raw_gma(sensor, 1);           // RAW GMA: 1 (활성화)
    sensor->set_lenc(sensor, 0);              // 렌즈 보정: 1 (활성화)
    sensor->set_hmirror(sensor, 0);           // 수평 미러: 0 (비활성화)
    sensor->set_vflip(sensor, 0);             // 수직 플립: 0 (비활성화)
    sensor->set_dcw(sensor, 0);               // DCW: 1 (활성화)
    sensor->set_colorbar(sensor, 0);          // 컬러 바: 0 (비활성화)
    
    Serial.println("카메라 초기화 완료!");
    return true;
}

/**
 * 카메라 프레임 캡처 함수
 * @return camera_fb_t* 프레임 버퍼 포인터 (실패 시 NULL)
 */
camera_fb_t* captureFrame() {
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("프레임 캡처 실패!");
        return NULL;
    }
    return fb;
}

/**
 * 프레임 버퍼 반환 함수
 * @param fb 반환할 프레임 버퍼 포인터
 */
void returnFrameBuffer(camera_fb_t* fb) {
    if (fb) {
        esp_camera_fb_return(fb);
    }
}

#endif // CAMERA_INIT_H

