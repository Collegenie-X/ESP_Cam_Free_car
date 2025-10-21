#ifndef CAMERA_STREAM_HANDLER_H
#define CAMERA_STREAM_HANDLER_H

#include "esp_camera.h"
#include "esp_http_server.h"

// MJPEG 스트림 경계 문자열
#define STREAM_BOUNDARY "123456789000000000000987654321"
#define STREAM_CONTENT_TYPE "multipart/x-mixed-replace;boundary=" STREAM_BOUNDARY
#define STREAM_BOUNDARY_PART "_STREAM_PART: " STREAM_BOUNDARY "\r\n"

/**
 * 단일 프레임 전송 함수
 * @param req HTTP 요청 핸들러
 * @param fb 프레임 버퍼 포인터
 * @return 전송 성공 시 ESP_OK, 실패 시 ESP_FAIL
 */
esp_err_t sendFrame(httpd_req_t *req, camera_fb_t *fb) {
    if (!fb) {
        Serial.println("프레임 버퍼가 NULL입니다!");
        return ESP_FAIL;
    }
    
    // 프레임 헤더 작성
    char part_buf[64];
    snprintf(part_buf, 64, 
             "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n",
             (uint32_t)(fb->len));
    
    // 경계 문자열 전송
    if (httpd_resp_send_chunk(req, STREAM_BOUNDARY_PART, strlen(STREAM_BOUNDARY_PART)) != ESP_OK) {
        return ESP_FAIL;
    }
    
    // 프레임 헤더 전송
    if (httpd_resp_send_chunk(req, part_buf, strlen(part_buf)) != ESP_OK) {
        return ESP_FAIL;
    }
    
    // 프레임 데이터 전송
    if (httpd_resp_send_chunk(req, (const char *)fb->buf, fb->len) != ESP_OK) {
        return ESP_FAIL;
    }
    
    return ESP_OK;
}

/**
 * 스트리밍 핸들러 함수
 * @param req HTTP 요청 핸들러
 * @return 핸들러 처리 결과
 */
esp_err_t streamHandler(httpd_req_t *req) {
    camera_fb_t *fb = NULL;
    esp_err_t res = ESP_OK;
    
    Serial.println("스트리밍 시작...");
    
    // 응답 헤더 설정
    httpd_resp_set_type(req, STREAM_CONTENT_TYPE);
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    
    // 스트리밍 루프
    while (true) {
        // 프레임 캡처
        fb = esp_camera_fb_get();
        if (!fb) {
            Serial.println("프레임 캡처 실패!");
            res = ESP_FAIL;
            break;
        }
        
        // 프레임 전송
        if (sendFrame(req, fb) != ESP_OK) {
            esp_camera_fb_return(fb);
            res = ESP_FAIL;
            break;
        }
        
        // 프레임 버퍼 반환
        esp_camera_fb_return(fb);
        fb = NULL;
    }
    
    // 정리
    if (fb) {
        esp_camera_fb_return(fb);
    }
    
    Serial.println("스트리밍 종료");
    return res;
}

/**
 * 단일 이미지 캡처 핸들러 함수
 * @param req HTTP 요청 핸들러
 * @return 핸들러 처리 결과
 */
esp_err_t captureHandler(httpd_req_t *req) {
    camera_fb_t *fb = NULL;
    esp_err_t res = ESP_OK;
    
    Serial.println("이미지 캡처 요청");
    
    // 프레임 캡처
    fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("프레임 캡처 실패!");
        httpd_resp_send_500(req);
        return ESP_FAIL;
    }
    
    // 응답 헤더 설정
    httpd_resp_set_type(req, "image/jpeg");
    httpd_resp_set_hdr(req, "Content-Disposition", "inline; filename=capture.jpg");
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    
    // 이미지 데이터 전송
    res = httpd_resp_send(req, (const char *)fb->buf, fb->len);
    
    // 프레임 버퍼 반환
    esp_camera_fb_return(fb);
    
    Serial.println("이미지 캡처 완료");
    return res;
}

#endif // CAMERA_STREAM_HANDLER_H

