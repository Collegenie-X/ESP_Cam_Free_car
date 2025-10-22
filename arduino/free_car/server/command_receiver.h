#ifndef COMMAND_RECEIVER_H
#define COMMAND_RECEIVER_H

#include "esp_http_server.h"
#include "../motor/motor_controller.h"
#include "../motor/motor_command.h"
#include "../led/led_controller.h"
#include "../camera/camera_control.h"
#include <Arduino.h>

/**
 * 제어 명령 수신 핸들러 함수
 * URL: /control?cmd=[left|right|center|stop]
 * @param req HTTP 요청 핸들러
 * @return 핸들러 처리 결과
 */
esp_err_t controlCommandHandler(httpd_req_t *req) {
    // URL 파라미터 파싱을 위한 버퍼
    char buf[100];
    size_t buf_len;
    
    // Query String 길이 확인
    buf_len = httpd_req_get_url_query_len(req) + 1;
    if (buf_len > 1) {
        if (httpd_req_get_url_query_str(req, buf, buf_len) == ESP_OK) {
            // cmd 파라미터 추출
            char cmd_param[32];
            if (httpd_query_key_value(buf, "cmd", cmd_param, sizeof(cmd_param)) == ESP_OK) {
                // 명령 파싱
                String cmdString = String(cmd_param);
                CommandType cmd = parseCommand(cmdString);
                
                // Early return: 알 수 없는 명령
                if (cmd == UNKNOWN) {
                    httpd_resp_set_status(req, "400 Bad Request");
                    httpd_resp_send(req, "Unknown command", HTTPD_RESP_USE_STRLEN);
                    return ESP_OK;
                }
                
                // 명령 실행
                executeCommand(cmd);
                
                // 응답 전송
                String response = "Command executed: " + commandToString(cmd);
                httpd_resp_set_type(req, "text/plain");
                httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
                httpd_resp_send(req, response.c_str(), HTTPD_RESP_USE_STRLEN);
                
                Serial.printf("명령 수신: %s\n", cmd_param);
                return ESP_OK;
            }
        }
    }
    
    // 파라미터가 없는 경우
    httpd_resp_set_status(req, "400 Bad Request");
    httpd_resp_send(req, "Missing cmd parameter", HTTPD_RESP_USE_STRLEN);
    return ESP_OK;
}

/**
 * LED 제어 핸들러 함수
 * URL: /led?state=[on|off|toggle]
 * @param req HTTP 요청 핸들러
 * @return 핸들러 처리 결과
 */
esp_err_t ledControlHandler(httpd_req_t *req) {
    // URL 파라미터 파싱을 위한 버퍼
    char buf[100];
    size_t buf_len;
    
    // Query String 길이 확인
    buf_len = httpd_req_get_url_query_len(req) + 1;
    if (buf_len > 1) {
        if (httpd_req_get_url_query_str(req, buf, buf_len) == ESP_OK) {
            // state 파라미터 추출
            char state_param[32];
            if (httpd_query_key_value(buf, "state", state_param, sizeof(state_param)) == ESP_OK) {
                // LED 상태 문자열을 소문자로 변환
                String stateString = String(state_param);
                stateString.toLowerCase();
                stateString.trim();
                
                // LED 제어 실행
                if (stateString == "on") {
                    turnOnLED();
                } else if (stateString == "off") {
                    turnOffLED();
                } else if (stateString == "toggle") {
                    toggleLED();
                } else {
                    // 알 수 없는 상태
                    httpd_resp_set_status(req, "400 Bad Request");
                    httpd_resp_send(req, "Unknown LED state. Use: on, off, or toggle", HTTPD_RESP_USE_STRLEN);
                    return ESP_OK;
                }
                
                // 응답 전송
                String response = "LED state: ";
                response += getLEDState() ? "ON" : "OFF";
                httpd_resp_set_type(req, "text/plain");
                httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
                httpd_resp_send(req, response.c_str(), HTTPD_RESP_USE_STRLEN);
                
                Serial.printf("LED 제어 수신: %s\n", state_param);
                return ESP_OK;
            }
        }
    }
    
    // 파라미터가 없는 경우
    httpd_resp_set_status(req, "400 Bad Request");
    httpd_resp_send(req, "Missing state parameter", HTTPD_RESP_USE_STRLEN);
    return ESP_OK;
}

/**
 * 상태 확인 핸들러 함수
 * URL: /status
 * @param req HTTP 요청 핸들러
 * @return 핸들러 처리 결과
 */
esp_err_t statusHandler(httpd_req_t *req) {
    // 카메라 센서 정보 가져오기
    sensor_t* sensor = esp_camera_sensor_get();
    
    // JSON 형식으로 상태 정보 생성
    String json = "{\n";
    json += "  \"wifi_connected\": true,\n";
    json += "  \"ip_address\": \"" + WiFi.localIP().toString() + "\",\n";
    json += "  \"camera_status\": \"ok\",\n";
    json += "  \"motor_status\": \"";
    json += isMotorRunning() ? "running" : "stopped";
    json += "\",\n";
    json += "  \"current_command\": \"" + commandToString(getCurrentCommand()) + "\",\n";
    json += "  \"led_state\": \"";
    json += getLEDState() ? "on" : "off";
    json += "\",\n";
    json += "  \"speed\": ";
    json += String(getMotorSpeed());
    json += ",\n";
    
    // 카메라 센서 설정 추가
    json += "  \"camera_settings\": {\n";
    if (sensor) {
        json += "    \"brightness\": " + String(sensor->status.brightness) + ",\n";
        json += "    \"contrast\": " + String(sensor->status.contrast) + ",\n";
        json += "    \"saturation\": " + String(sensor->status.saturation) + ",\n";
        json += "    \"agc_gain\": " + String(sensor->status.agc_gain) + ",\n";
        json += "    \"gainceiling\": " + String(sensor->status.gainceiling) + ",\n";
        json += "    \"aec2\": " + String(sensor->status.aec2) + ",\n";
        json += "    \"hmirror\": " + String(sensor->status.hmirror) + ",\n";
        json += "    \"vflip\": " + String(sensor->status.vflip) + "\n";
    } else {
        json += "    \"error\": \"sensor not available\"\n";
    }
    json += "  }\n";
    json += "}";
    
    // 응답 전송
    httpd_resp_set_type(req, "application/json");
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    httpd_resp_send(req, json.c_str(), HTTPD_RESP_USE_STRLEN);
    
    return ESP_OK;
}

/**
 * 속도 제어 핸들러 함수
 * URL: /speed?op=[plus|minus]&step=10
 */
esp_err_t speedControlHandler(httpd_req_t *req) {
    char buf[100];
    size_t buf_len = httpd_req_get_url_query_len(req) + 1;
    if (buf_len > 1 && httpd_req_get_url_query_str(req, buf, buf_len) == ESP_OK) {
        char op_param[16];
        char step_param[16];
        String op = "";
        int step = 10;
        if (httpd_query_key_value(buf, "op", op_param, sizeof(op_param)) == ESP_OK) {
            op = String(op_param);
            op.toLowerCase();
            op.trim();
        }
        if (httpd_query_key_value(buf, "step", step_param, sizeof(step_param)) == ESP_OK) {
            step = atoi(step_param);
            if (step < 1) step = 1;
            if (step > 100) step = 100; // 과도한 증감 방지
        }

        int after = getMotorSpeed();
        if (op == "plus") {
            after = increaseMotorSpeed(step);
        } else if (op == "minus") {
            after = decreaseMotorSpeed(step);
        } else {
            httpd_resp_set_status(req, "400 Bad Request");
            httpd_resp_send(req, "Unknown op. Use plus or minus", HTTPD_RESP_USE_STRLEN);
            return ESP_OK;
        }

        String resp = String("speed=") + String(after);
        httpd_resp_set_type(req, "text/plain");
        httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
        httpd_resp_send(req, resp.c_str(), HTTPD_RESP_USE_STRLEN);
        return ESP_OK;
    }

    httpd_resp_set_status(req, "400 Bad Request");
    httpd_resp_send(req, "Missing op parameter", HTTPD_RESP_USE_STRLEN);
    return ESP_OK;
}

/**
 * 카메라 센서 제어 핸들러 함수
 * URL: /camera?param=[brightness|contrast|saturation|agc_gain|gainceiling|aec2|hmirror|vflip]&value=N
 * 또는 /camera?get=settings (현재 설정값 조회)
 */
esp_err_t cameraControlHandler(httpd_req_t *req) {
    char buf[150];
    size_t buf_len = httpd_req_get_url_query_len(req) + 1;
    
    if (buf_len > 1 && httpd_req_get_url_query_str(req, buf, buf_len) == ESP_OK) {
        // 설정값 조회 요청
        char get_param[16];
        if (httpd_query_key_value(buf, "get", get_param, sizeof(get_param)) == ESP_OK) {
            String getStr = String(get_param);
            getStr.toLowerCase();
            if (getStr == "settings") {
                String settings = getCameraSettings();
                httpd_resp_set_type(req, "application/json");
                httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
                httpd_resp_send(req, settings.c_str(), HTTPD_RESP_USE_STRLEN);
                return ESP_OK;
            }
        }
        
        // 설정값 변경 요청
        char param_name[32];
        char value_str[16];
        
        if (httpd_query_key_value(buf, "param", param_name, sizeof(param_name)) != ESP_OK) {
            httpd_resp_set_status(req, "400 Bad Request");
            httpd_resp_send(req, "Missing param parameter", HTTPD_RESP_USE_STRLEN);
            return ESP_OK;
        }
        
        if (httpd_query_key_value(buf, "value", value_str, sizeof(value_str)) != ESP_OK) {
            httpd_resp_set_status(req, "400 Bad Request");
            httpd_resp_send(req, "Missing value parameter", HTTPD_RESP_USE_STRLEN);
            return ESP_OK;
        }
        
        String param = String(param_name);
        param.toLowerCase();
        param.trim();
        
        int value = atoi(value_str);
        bool success = false;
        String response = "";
        
        // 파라미터별 처리
        if (param == "brightness") {
            success = setCameraBrightness(value);
            response = "brightness=" + String(value);
        } else if (param == "contrast") {
            success = setCameraContrast(value);
            response = "contrast=" + String(value);
        } else if (param == "saturation") {
            success = setCameraSaturation(value);
            response = "saturation=" + String(value);
        } else if (param == "agc_gain") {
            success = setCameraAgcGain(value);
            response = "agc_gain=" + String(value);
        } else if (param == "gainceiling") {
            success = setCameraGainCeiling(value);
            response = "gainceiling=" + String(value);
        } else if (param == "aec2") {
            success = setCameraAec2(value);
            response = "aec2=" + String(value);
        } else if (param == "hmirror") {
            success = setCameraHmirror(value);
            response = "hmirror=" + String(value);
        } else if (param == "vflip") {
            success = setCameraVflip(value);
            response = "vflip=" + String(value);
        } else {
            httpd_resp_set_status(req, "400 Bad Request");
            httpd_resp_send(req, "Unknown param. Use: brightness, contrast, saturation, agc_gain, gainceiling, aec2, hmirror, vflip", HTTPD_RESP_USE_STRLEN);
            return ESP_OK;
        }
        
        if (success) {
            httpd_resp_set_type(req, "text/plain");
            httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
            httpd_resp_send(req, response.c_str(), HTTPD_RESP_USE_STRLEN);
        } else {
            httpd_resp_set_status(req, "500 Internal Server Error");
            httpd_resp_send(req, "Failed to set camera parameter", HTTPD_RESP_USE_STRLEN);
        }
        
        return ESP_OK;
    }
    
    // 파라미터가 없는 경우 - 현재 설정 반환
    String settings = getCameraSettings();
    httpd_resp_set_type(req, "application/json");
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    httpd_resp_send(req, settings.c_str(), HTTPD_RESP_USE_STRLEN);
    return ESP_OK;
}

/**
 * 루트 페이지 핸들러 함수
 * URL: /
 * @param req HTTP 요청 핸들러
 * @return 핸들러 처리 결과
 */
esp_err_t indexHandler(httpd_req_t *req) {
    // 간단한 HTML 페이지
    const char html[] = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Free Car - 자율주행차</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f0f0f0;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .container {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .stream-container {
            text-align: center;
            margin: 20px 0;
        }
        img {
            max-width: 100%;
            border-radius: 5px;
        }
        .controls {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin: 20px 0;
        }
        button {
            padding: 15px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            background-color: #4CAF50;
            color: white;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #45a049;
        }
        button:active {
            background-color: #3d8b40;
        }
        .stop-btn {
            background-color: #f44336;
        }
        .stop-btn:hover {
            background-color: #da190b;
        }
        .led-section {
            margin: 20px 0;
            padding: 15px;
            background-color: #fff9e6;
            border-left: 4px solid #ffc107;
            border-radius: 5px;
        }
        .led-controls {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-top: 10px;
        }
        .led-btn {
            background-color: #ffc107;
            color: #000;
        }
        .led-btn:hover {
            background-color: #ffb300;
        }
        .led-btn-off {
            background-color: #757575;
        }
        .led-btn-off:hover {
            background-color: #616161;
        }
        .info {
            margin-top: 20px;
            padding: 10px;
            background-color: #e7f3ff;
            border-left: 4px solid #2196F3;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚗 Free Car - 자율주행차</h1>
        
        <div class="stream-container">
            <h3>카메라 스트림</h3>
            <img id="stream" src="/stream" alt="Camera Stream">
        </div>
        
        <div class="controls">
            <button onclick="sendCommand('left')">⬅️ 좌회전</button>
            <button onclick="sendCommand('center')">⬆️ 전진</button>
            <button onclick="sendCommand('right')">➡️ 우회전</button>
            <button onclick="sendCommand('stop')" class="stop-btn" style="grid-column: span 3;">🛑 정지</button>
        </div>
        
        <div class="led-section">
            <h3>💡 LED 제어</h3>
            <div class="led-controls">
                <button onclick="controlLED('on')" class="led-btn">💡 LED 켜기</button>
                <button onclick="controlLED('off')" class="led-btn-off">🌑 LED 끄기</button>
                <button onclick="controlLED('toggle')" class="led-btn">🔄 LED 토글</button>
            </div>
        </div>
        
        <div class="info">
            <h3>ℹ️ API 엔드포인트</h3>
            <ul>
                <li><strong>GET /stream</strong> - MJPEG 영상 스트리밍</li>
                <li><strong>GET /control?cmd=[left|right|center|stop]</strong> - 모터 제어</li>
                <li><strong>GET /led?state=[on|off|toggle]</strong> - LED 제어</li>
                <li><strong>GET /status</strong> - 상태 확인 (JSON)</li>
                <li><strong>GET /capture</strong> - 단일 이미지 캡처</li>
            </ul>
        </div>
    </div>
    
    <script>
        function sendCommand(cmd) {
            fetch('/control?cmd=' + cmd)
                .then(response => response.text())
                .then(data => console.log('Response:', data))
                .catch(error => console.error('Error:', error));
        }
        
        function controlLED(state) {
            fetch('/led?state=' + state)
                .then(response => response.text())
                .then(data => {
                    console.log('LED Response:', data);
                    // LED 상태를 화면에 표시 (선택사항)
                })
                .catch(error => console.error('LED Error:', error));
        }
    </script>
</body>
</html>
)rawliteral";
    
    httpd_resp_set_type(req, "text/html");
    httpd_resp_send(req, html, HTTPD_RESP_USE_STRLEN);
    
    return ESP_OK;
}

#endif // COMMAND_RECEIVER_H

