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
    
    // 카메라 설정
    config.xclk_freq_hz = 20000000;           // XCLK 주파수 (20MHz)
    config.ledc_timer = LEDC_TIMER_0;         // LEDC 타이머
    config.ledc_channel = LEDC_CHANNEL_0;     // LEDC 채널
    
    config.pixel_format = PIXFORMAT_JPEG;     // JPEG 포맷
    config.frame_size = FRAMESIZE_VGA;        // VGA 해상도 (640x480)
    config.jpeg_quality = 12;                 // JPEG 품질 (0-63, 낮을수록 고품질)
    config.fb_count = 1;                      // 프레임 버퍼 개수
    
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
    
    // 센서 설정 최적화
    sensor->set_brightness(sensor, 0);        // 밝기: -2 ~ 2
    sensor->set_contrast(sensor, 0);          // 대비: -2 ~ 2
    sensor->set_saturation(sensor, 0);        // 채도: -2 ~ 2
    sensor->set_special_effect(sensor, 0);    // 특수 효과: 0 (없음)
    sensor->set_whitebal(sensor, 1);          // 화이트 밸런스: 1 (자동)
    sensor->set_awb_gain(sensor, 1);          // AWB 게인: 1 (활성화)
    sensor->set_wb_mode(sensor, 0);           // WB 모드: 0 (자동)
    sensor->set_exposure_ctrl(sensor, 1);     // 노출 제어: 1 (자동)
    sensor->set_aec2(sensor, 0);              // AEC2: 0 (비활성화)
    sensor->set_gain_ctrl(sensor, 1);         // 게인 제어: 1 (자동)
    sensor->set_agc_gain(sensor, 0);          // AGC 게인: 0
    sensor->set_gainceiling(sensor, (gainceiling_t)0);  // 게인 상한
    sensor->set_bpc(sensor, 0);               // BPC: 0 (비활성화)
    sensor->set_wpc(sensor, 1);               // WPC: 1 (활성화)
    sensor->set_raw_gma(sensor, 1);           // RAW GMA: 1 (활성화)
    sensor->set_lenc(sensor, 1);              // 렌즈 보정: 1 (활성화)
    sensor->set_hmirror(sensor, 0);           // 수평 미러: 0 (비활성화)
    sensor->set_vflip(sensor, 0);             // 수직 플립: 0 (비활성화)
    sensor->set_dcw(sensor, 1);               // DCW: 1 (활성화)
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

