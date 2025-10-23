#ifndef CAMERA_STREAM_HANDLER_H
#define CAMERA_STREAM_HANDLER_H

#include "esp_camera.h"
#include "esp_http_server.h"
#include "../config/stream_config.h"

// MJPEG 스트림 경계 문자열
// 표준 MJPEG 경계 및 콘텐츠 타입 정의
#define STREAM_BOUNDARY "frame"
#define STREAM_CONTENT_TYPE "multipart/x-mixed-replace; boundary=" STREAM_BOUNDARY
// 각 프레임 시작 시 전송되는 경계 문자열 ("--boundary\r\n")
#define STREAM_BOUNDARY_PART "--" STREAM_BOUNDARY "\r\n"

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

    // 프레임 종료를 위한 CRLF 전송
    if (httpd_resp_send_chunk(req, "\r\n", 2) != ESP_OK) {
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
    unsigned long startMem = ESP.getFreeHeap();
    Serial.printf("시작 메모리: %lu bytes\n", startMem);
    
    // 스트림 설정 출력
    if (STREAM_DEBUG_ENABLED) {
        printStreamConfig();
    }
    
    // 응답 헤더 설정
    httpd_resp_set_type(req, STREAM_CONTENT_TYPE);
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    httpd_resp_set_hdr(req, "Cache-Control", "no-cache, no-store, must-revalidate");
    httpd_resp_set_hdr(req, "Pragma", "no-cache");
    httpd_resp_set_hdr(req, "Expires", "0");
    
    // 프레임 카운터 (디버깅용)
    unsigned long frameCount = 0;
    unsigned long lastMemCheck = millis();
    
    // 스트리밍 루프
    while (true) {
        // ✅ 프레임 캡처 전 이전 버퍼가 남아있으면 제거 (메모리 누수 방지)
        if (fb) {
            esp_camera_fb_return(fb);
            fb = NULL;
        }
        
        // 프레임 캡처
        fb = esp_camera_fb_get();
        if (!fb) {
            Serial.println("⚠️ 프레임 캡처 실패!");
            // ✅ 실패 시 재시도 (일시적 문제 대응)
            delay(10);
            continue;
        }
        
        // 프레임 전송
        if (sendFrame(req, fb) != ESP_OK) {
            Serial.println("⚠️ 프레임 전송 실패 - 클라이언트 연결 종료");
            esp_camera_fb_return(fb);
            res = ESP_FAIL;
            break;
        }
        
        // 프레임 버퍼 즉시 반환 (메모리 확보)
        esp_camera_fb_return(fb);
        fb = NULL;
        
        frameCount++;
        
        // ✅ 주기적으로 메모리 상태 체크
        if (millis() - lastMemCheck > MEMORY_CHECK_INTERVAL) {
            lastMemCheck = millis();
            unsigned long currentMem = ESP.getFreeHeap();
            
            if (STREAM_DEBUG_ENABLED) {
                long memDiff = (long)currentMem - (long)startMem;
                Serial.printf("📊 프레임: %lu | 메모리: %lu bytes", 
                             frameCount, currentMem);
                
                if (memDiff > 0) {
                    Serial.printf(" (+%ld)\n", memDiff);
                } else {
                    Serial.printf(" (%ld)\n", memDiff);
                }
            }
            
            // ⚠️ 메모리 경고 및 위험 알림
            if (currentMem < MEMORY_CRITICAL_THRESHOLD) {
                Serial.println("🚨 위험: 메모리 심각 부족! 스트림 재시작 권장!");
            } else if (currentMem < MEMORY_WARNING_THRESHOLD) {
                Serial.println("⚠️ 경고: 메모리 부족! 모니터링 중...");
            }
        }
        
        // ✅ FPS 조절 (stream_config.h에서 설정)
        delay(STREAM_DELAY_MS);
        
        // ✅ 매 프레임마다 제어권 양보 (다른 HTTP 요청 처리 보장)
        if (frameCount % YIELD_INTERVAL_FRAMES == 0) {
            // 태스크 스케줄러에게 제어권 양보
            taskYIELD();
            // 추가 대기: 다른 HTTP 요청(모터 제어 등)이 처리될 시간 확보
            delay(EXTRA_YIELD_DELAY_MS);
        }
        
        // ✅ 주기적으로 메모리 정리 시간 제공
        if (frameCount % MEMORY_CLEANUP_INTERVAL == 0) {
            // 잠깐 대기하여 시스템이 메모리를 정리할 시간 제공
            delay(10);
        }
    }
    
    // 정리
    if (fb) {
        esp_camera_fb_return(fb);
        fb = NULL;
    }
    
    Serial.printf("스트리밍 종료 (총 프레임: %lu)\n", frameCount);
    return res;
}

/**
 * 단일 이미지 캡처 핸들러 함수
 * @param req HTTP 요청 핸들러
 * @return 핸들러 처리 결과
 */
esp_err_t captureHandler(httpd_req_t *req) {
    static uint32_t last_frame_time = 0;
    static camera_fb_t *last_fb = NULL;
    camera_fb_t *fb = NULL;
    esp_err_t res = ESP_OK;
    
    // ✅ 이전 프레임 버퍼 정리
    if (last_fb) {
        esp_camera_fb_return(last_fb);
        last_fb = NULL;
    }
    
    // ✅ 프레임 캡처 전 짧은 대기 (센서 안정화)
    uint32_t current_time = millis();
    if (current_time - last_frame_time < 50) {  // 최소 50ms 간격
        delay(5);  // 짧은 대기
    }
    
    // ✅ 프레임 캡처 (빠른 실패 처리)
    fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("⚠️ 캡처 실패!");
        httpd_resp_send_500(req);
        return ESP_FAIL;
    }
    
    // ✅ Early return: 빈 프레임 체크
    if (fb->len == 0 || fb->buf == NULL || fb->len > 65535) {  // 크기 제한 추가
        Serial.println("⚠️ 빈 프레임 또는 크기 초과!");
        esp_camera_fb_return(fb);
        httpd_resp_send_500(req);
        return ESP_FAIL;
    }
    
    last_frame_time = current_time;
    
    // ✅ 응답 헤더 최적화 (단순화)
    httpd_resp_set_type(req, "image/jpeg");
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    httpd_resp_set_hdr(req, "Connection", "keep-alive");
    httpd_resp_set_hdr(req, "Keep-Alive", "timeout=5, max=100");
    httpd_resp_set_hdr(req, "Cache-Control", "no-store, no-cache, must-revalidate");
    
    // ✅ 이미지 데이터 전송 (즉시 전송)
    res = httpd_resp_send(req, (const char *)fb->buf, fb->len);
    
    // ✅ 프레임 버퍼 즉시 반환 (메모리 확보)
    esp_camera_fb_return(fb);
    fb = NULL;
    
    // ✅ 전송 실패 시 빠른 복구
    if (res != ESP_OK) {
        Serial.println("⚠️ 전송 실패!");
        return ESP_FAIL;
    }
    
    return ESP_OK;
}

#endif // CAMERA_STREAM_HANDLER_H

