# 🎯 AI 객체 감지 데모 사용 가이드

## 완성! ✅

ESP32-CAM에서 캡처한 이미지를 YOLO 모델로 분석하여 **Label**과 **Rect 좌표**를 보여주는 기능이 완성되었습니다!

---

## 🚀 빠른 시작

### 1. 서버 실행
```bash
cd frontend
source venv/bin/activate
python app.py
```

### 2. 웹 브라우저에서 AI 데모 페이지 열기
```
http://localhost:5002/ai-demo
```

### 3. 버튼 클릭!
- **🎯 객체 감지**: ESP32-CAM 이미지에서 사람, 자동차 등 80종류 객체 감지
- **🛣️ 차선 감지**: 도로 차선 인식
- **🔍 종합 분석**: 객체 + 차선 동시 감지

---

## 📊 결과 확인

### 왼쪽 패널: 분석 이미지
- Bounding Box가 그려진 이미지
- 각 객체 주위에 녹색 사각형
- 레이블과 신뢰도 표시

### 오른쪽 패널: 상세 정보
```
1. person
   신뢰도: 92.0%
   Rect 좌표:
   x1: 100, y1: 150
   x2: 300, y2: 450
   
   BBox:
   x: 100, y: 150
   width: 200, height: 300
```

---

## 🔥 주요 기능

### ✅ PyTorch 2.6+ 호환
- `weights_only` 문제 자동 해결
- 안전하게 YOLO 모델 로드

### ✅ 실시간 분석
- ESP32-CAM에서 이미지 캡처
- YOLO로 즉시 분석
- 결과 시각화

### ✅ 80종류 객체 감지
- 사람, 자동차, 동물
- 신호등, 표지판
- 생활용품 등

### ✅ Rect 좌표 제공
- x1, y1: 좌상단
- x2, y2: 우하단
- width, height 포함

---

## 💡 API 사용 예시

### JavaScript
```javascript
// 객체 감지
const response = await fetch('/api/ai/detect');
const data = await response.json();

data.objects.forEach(obj => {
    console.log(`${obj.label}: ${obj.confidence}`);
    console.log(`Rect: (${obj.rect.x1}, ${obj.rect.y1}) → (${obj.rect.x2}, ${obj.rect.y2})`);
});
```

### Python
```python
import requests

# 객체 감지
r = requests.get('http://localhost:5002/api/ai/detect')
data = r.json()

for obj in data['objects']:
    print(f"{obj['label']}: {obj['confidence']:.2f}")
    print(f"  Rect: ({obj['rect']['x1']}, {obj['rect']['y1']}) → ({obj['rect']['x2']}, {obj['rect']['y2']})")
```

---

## 🎯 자율주행 활용

### 장애물 회피
```python
response = requests.get('http://localhost:5002/api/ai/detect')
data = response.json()

# 전방 중앙에 객체가 있는지 확인
for obj in data['objects']:
    center_x = (obj['rect']['x1'] + obj['rect']['x2']) / 2
    if 100 < center_x < 220:  # 이미지 중앙
        print(f"장애물 감지: {obj['label']}")
        # ESP32에 정지 명령
        requests.get('http://192.168.0.65/control?cmd=stop')
```

### 차선 유지
```python
response = requests.get('http://localhost:5002/api/ai/lanes')
data = response.json()

offset = data['center_offset']
if offset < -20:
    command = "left"
elif offset > 20:
    command = "right"
else:
    command = "center"

requests.get(f'http://192.168.0.65/control?cmd={command}')
```

---

## 📸 스크린샷

```
┌─────────────────────────────────────┐
│  📹 분석 결과 이미지                 │
│                                     │
│    [person]                         │
│     0.92                            │
│   ┌─────────┐                       │
│   │         │                       │
│   │  사람   │                       │
│   │         │                       │
│   └─────────┘                       │
│                                     │
│         [car]                       │
│          0.85                       │
│     ┌───────────┐                   │
│     │  자동차   │                   │
│     └───────────┘                   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  📊 분석 결과                        │
│                                     │
│  총 감지된 객체: 2개                │
│  ┌───────────────────────────────┐ │
│  │ person: 1개                   │ │
│  │ car: 1개                      │ │
│  └───────────────────────────────┘ │
│                                     │
│  1. person                          │
│     신뢰도: 92.0%                   │
│     ┌───────────────────────────┐ │
│     │ Rect:                     │ │
│     │ x1: 100, y1: 150         │ │
│     │ x2: 300, y2: 450         │ │
│     │                           │ │
│     │ BBox:                     │ │
│     │ x: 100, y: 150           │ │
│     │ width: 200, height: 300  │ │
│     └───────────────────────────┘ │
│                                     │
│  2. car                             │
│     신뢰도: 85.0%                   │
│     ...                             │
└─────────────────────────────────────┘
```

---

## 🔧 문제 해결

### YOLO 모델 로드 에러?
- ✅ 이미 해결됨! PyTorch 2.6+ 자동 호환

### 객체가 감지되지 않음?
- 조명을 밝게 하세요
- 카메라 각도를 조정하세요
- 신뢰도 임계값을 낮춰보세요 (0.3~0.5)

### 느린 분석 속도?
- 정상입니다 (CPU: 1-3초/이미지)
- GPU 사용 시 0.1-0.5초

---

## 📚 관련 API

### GET /api/ai/detect
객체 감지 API
- Query: `?draw=true` (이미지 반환)
- Response: JSON (객체 리스트 + 요약)

### GET /api/ai/lanes
차선 감지 API  
- Query: `?draw=true` (이미지 반환)
- Response: JSON (차선 리스트 + 오프셋)

### GET /api/ai/analyze
종합 분석 API
- Query: `?draw=true` (이미지 반환)
- Response: JSON (객체 + 차선)

---

## 🎉 완성된 기능

✅ YOLO 모델 통합 완료  
✅ PyTorch 2.6+ 호환 문제 해결  
✅ ESP32-CAM 이미지 실시간 분석  
✅ Label + Rect 좌표 제공  
✅ 웹 UI 데모 페이지  
✅ REST API 제공  
✅ 차선 감지 기능  
✅ 종합 분석 기능  

---

**이제 ESP32-CAM으로 찍은 사진을 AI로 분석할 수 있습니다!** 🚀

