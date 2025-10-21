
## 🔌 API 사용법

### 영상 스트리밍
```
GET http://192.168.1.100/stream
```

### 모터 제어
```
GET http://192.168.1.100/control?cmd=left     # 좌회전
GET http://192.168.1.100/control?cmd=right    # 우회전
GET http://192.168.1.100/control?cmd=center   # 전진
GET http://192.168.1.100/control?cmd=stop     # 정지
```

### LED 제어
```
GET http://192.168.1.100/led?state=on          # LED 켜기
GET http://192.168.1.100/led?state=off         # LED 끄기
GET http://192.168.1.100/led?state=toggle      # LED 토글
```

### 상태 확인
```
GET http://192.168.1.100/status
응답:
{
  "wifi_connected": true,
  "ip_address": "192.168.1.100",
  "camera_status": "ok",
  "motor_status": "ok",
  "current_command": "CENTER",
  "led_state": "on"
}
```