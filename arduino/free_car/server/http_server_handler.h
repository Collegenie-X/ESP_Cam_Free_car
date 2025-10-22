#ifndef HTTP_SERVER_HANDLER_H
#define HTTP_SERVER_HANDLER_H

#include "esp_http_server.h"
#include "../camera/camera_stream_handler.h"
#include "command_receiver.h"

// HTTP 서버 핸들
httpd_handle_t server = NULL;

/**
 * URI 핸들러 등록 함수
 */
void registerUriHandlers() {
    // 1. 루트 페이지 핸들러 등록
    httpd_uri_t index_uri = {
        .uri       = "/",
        .method    = HTTP_GET,
        .handler   = indexHandler,
        .user_ctx  = NULL
    };
    httpd_register_uri_handler(server, &index_uri);
    Serial.println("URI 등록: /");
    
    // 2. 스트리밍 핸들러 등록
    httpd_uri_t stream_uri = {
        .uri       = "/stream",
        .method    = HTTP_GET,
        .handler   = streamHandler,
        .user_ctx  = NULL
    };
    httpd_register_uri_handler(server, &stream_uri);
    Serial.println("URI 등록: /stream");
    
    // 3. 이미지 캡처 핸들러 등록
    httpd_uri_t capture_uri = {
        .uri       = "/capture",
        .method    = HTTP_GET,
        .handler   = captureHandler,
        .user_ctx  = NULL
    };
    httpd_register_uri_handler(server, &capture_uri);
    Serial.println("URI 등록: /capture");
    
    // 4. 제어 명령 핸들러 등록
    httpd_uri_t control_uri = {
        .uri       = "/control",
        .method    = HTTP_GET,
        .handler   = controlCommandHandler,
        .user_ctx  = NULL
    };
    httpd_register_uri_handler(server, &control_uri);
    Serial.println("URI 등록: /control");
    
    // 5. LED 제어 핸들러 등록
    httpd_uri_t led_uri = {
        .uri       = "/led",
        .method    = HTTP_GET,
        .handler   = ledControlHandler,
        .user_ctx  = NULL
    };
    httpd_register_uri_handler(server, &led_uri);
    Serial.println("URI 등록: /led");
    
    // 6. 상태 확인 핸들러 등록
    httpd_uri_t status_uri = {
        .uri       = "/status",
        .method    = HTTP_GET,
        .handler   = statusHandler,
        .user_ctx  = NULL
    };
    httpd_register_uri_handler(server, &status_uri);
    Serial.println("URI 등록: /status");

    // 7. 속도 제어 핸들러 등록
    httpd_uri_t speed_uri = {
        .uri       = "/speed",
        .method    = HTTP_GET,
        .handler   = speedControlHandler,
        .user_ctx  = NULL
    };
    httpd_register_uri_handler(server, &speed_uri);
    Serial.println("URI 등록: /speed");
    
    // 8. 카메라 센서 제어 핸들러 등록
    httpd_uri_t camera_uri = {
        .uri       = "/camera",
        .method    = HTTP_GET,
        .handler   = cameraControlHandler,
        .user_ctx  = NULL
    };
    httpd_register_uri_handler(server, &camera_uri);
    Serial.println("URI 등록: /camera");
}

/**
 * HTTP 서버 시작 함수
 * @return 서버 시작 성공 시 true, 실패 시 false
 */
bool startHttpServer() {
    Serial.println("HTTP 서버 시작 중...");
    
    // 서버 설정
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = 80;                    // 포트 번호
    config.ctrl_port = 32768;                   // 제어 포트
    config.max_open_sockets = 10;               // 최대 소켓 수 (스트림+제어 동시 처리)
    config.max_uri_handlers = 12;               // 최대 URI 핸들러 수
    config.max_resp_headers = 8;                // 최대 응답 헤더 수
    config.backlog_conn = 5;                    // 백로그 연결 수
    config.lru_purge_enable = true;             // LRU 제거 활성화 (오래된 연결 자동 정리)
    config.recv_wait_timeout = 5;               // 수신 대기 타임아웃 (초)
    config.send_wait_timeout = 5;               // 전송 대기 타임아웃 (초)
    config.stack_size = 8192;                   // 핸들러 스택 크기 증가 (동시 처리 개선)
    
    // 서버 시작
    if (httpd_start(&server, &config) != ESP_OK) {
        Serial.println("HTTP 서버 시작 실패!");
        return false;
    }
    
    // URI 핸들러 등록
    registerUriHandlers();
    
    Serial.println("HTTP 서버 시작 완료!");
    Serial.printf("서버 주소: http://%s\n", WiFi.localIP().toString().c_str());
    
    return true;
}

/**
 * HTTP 서버 정지 함수
 */
void stopHttpServer() {
    if (server != NULL) {
        httpd_stop(server);
        server = NULL;
        Serial.println("HTTP 서버 정지");
    }
}

/**
 * 서버 실행 여부 확인 함수
 * @return 서버가 실행 중이면 true, 아니면 false
 */
bool isServerRunning() {
    return server != NULL;
}

#endif // HTTP_SERVER_HANDLER_H

