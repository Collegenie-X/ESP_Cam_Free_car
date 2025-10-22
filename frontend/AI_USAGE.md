# AI 기능 사용 가이드

## 📖 개요

ESP32-CAM 자율주행차에 **YOLO 객체 감지**와 **차선 인식** 기능이 추가되었습니다.

---

## 🔧 설치 방법

### 1. 필수 패키지 설치

```bash
# 가상환경 활성화
source venv/bin/activate  # Linux/Mac
# 또는
.\venv\Scripts\activate   # Windows

# AI 패키지 설치
pip install -r requirements.txt
```

### 2. YOLO 모델 다운로드

처음 실행 시 YOLOv8n 모델이 자동으로 다운로드됩니다 (~6MB).

---

## 📁 폴더 구조

```
frontend/
├── ai/                           # AI 분석 모듈
│   ├── __init__.py
│   ├── yolo_detector.py          # YOLO 객체 감지
│   └── lane_detector.py          # 차선 감지
│
└── routes/
    └── ai_routes.py              # AI API 라우트
```

---

## 🚀 API 사용법

### 1. 객체 감지 API

#### `GET /api/ai/detect`

ESP32-CAM 이미지에서 객체를 감지합니다.

**Query Parameters:**
- `draw` (optional): `true`면 Bounding Box가 그려진 이미지 반환

**예시 요청:**
```bash
# JSON 결과 받기
curl http://localhost:5000/api/ai/detect

# 이미지로 받기 (Bounding Box 표시)
curl http://localhost:5000/api/ai/detect?draw=true > result.jpg
```

**JSON 응답 예시:**
```json
{
  "success": true,
  "objects": [
    {
      "label": "person",
      "confidence": 0.92,
      "bbox": {
        "x": 100,
        "y": 150,
        "width": 200,
        "height": 300
      },
      "rect": {
        "x1": 100,
        "y1": 150,
        "x2": 300,
        "y2": 450
      }
    },
    {
      "label": "car",
      "confidence": 0.87,
      "bbox": {
        "x": 350,
        "y": 200,
        "width": 180,
        "height": 220
      },
      "rect": {
        "x1": 350,
        "y1": 200,
        "x2": 530,
        "y2": 420
      }
    }
  ],
  "summary": {
    "total_objects": 2,
    "classes": {
      "person": 1,
      "car": 1
    }
  }
}
```

---

### 2. 차선 감지 API

#### `GET /api/ai/lanes`

ESP32-CAM 이미지에서 차선을 감지합니다.

**Query Parameters:**
- `draw` (optional): `true`면 차선이 그려진 이미지 반환

**예시 요청:**
```bash
# JSON 결과 받기
curl http://localhost:5000/api/ai/lanes

# 이미지로 받기 (차선 표시)
curl http://localhost:5000/api/ai/lanes?draw=true > lanes.jpg
```

**JSON 응답 예시:**
```json
{
  "success": true,
  "lanes": [
    {
      "side": "left",
      "line": {
        "x1": 100,
        "y1": 400,
        "x2": 200,
        "y2": 300
      }
    },
    {
      "side": "right",
      "line": {
        "x1": 400,
        "y1": 400,
        "x2": 300,
        "y2": 300
      }
    }
  ],
  "center_offset": 15
}
```

**응답 필드 설명:**
- `lanes`: 감지된 차선 리스트
  - `side`: 차선 위치 (`"left"` 또는 `"right"`)
  - `line`: 차선 직선 좌표 (x1, y1: 시작점, x2, y2: 끝점)
- `center_offset`: 차선 중심과 이미지 중심의 오프셋 (픽셀)
  - 양수: 차선이 오른쪽으로 치우침
  - 음수: 차선이 왼쪽으로 치우침
  - `null`: 계산 불가 (차선 1개만 감지됨)

---

### 3. 종합 분석 API

#### `GET /api/ai/analyze`

객체 감지 + 차선 감지를 동시에 수행합니다.

**Query Parameters:**
- `draw` (optional): `true`면 모든 분석 결과가 그려진 이미지 반환

**예시 요청:**
```bash
# JSON 결과 받기
curl http://localhost:5000/api/ai/analyze

# 이미지로 받기 (객체 + 차선 표시)
curl http://localhost:5000/api/ai/analyze?draw=true > full_analysis.jpg
```

**JSON 응답 예시:**
```json
{
  "success": true,
  "objects": [...],
  "object_summary": {
    "total_objects": 2,
    "classes": {"person": 1, "car": 1}
  },
  "lanes": [...],
  "center_offset": 15
}
```

---

## 🧠 모듈 상세 설명

### 1. `YOLODetector` 클래스 (`ai/yolo_detector.py`)

YOLO 객체 감지를 담당하는 클래스입니다.

#### 주요 메서드

```python
from ai.yolo_detector import YOLODetector

# 초기화
detector = YOLODetector(
    model_path=None,  # None이면 기본 YOLOv8n 사용
    confidence_threshold=0.5  # 신뢰도 임계값
)

# 모델 로드 확인
if detector.is_ready():
    print("모델 준비 완료")

# 이미지에서 객체 감지 (numpy array)
import cv2
image = cv2.imread('test.jpg')
detections = detector.detect_objects(image)

# 바이트 데이터에서 객체 감지
with open('test.jpg', 'rb') as f:
    image_bytes = f.read()
detections = detector.detect_from_bytes(image_bytes)

# 감지 결과 그리기
result_image = detector.draw_detections(image, detections)

# 요약 정보
summary = detector.get_detection_summary(detections)
```

#### 반환 형식

각 감지된 객체는 다음 정보를 포함합니다:

- **label**: 객체 클래스 이름 (예: "person", "car", "dog" 등)
- **confidence**: 신뢰도 (0.0 ~ 1.0)
- **bbox**: Bounding Box (x, y, width, height)
- **rect**: 좌표 (x1, y1, x2, y2)

---

### 2. `LaneDetector` 클래스 (`ai/lane_detector.py`)

차선 감지를 담당하는 클래스입니다.

#### 주요 메서드

```python
from ai.lane_detector import LaneDetector

# 초기화
detector = LaneDetector(
    roi_top_ratio=0.6,  # ROI 상단 비율
    canny_low=50,  # Canny 하한값
    canny_high=150  # Canny 상한값
)

# 차선 감지
lanes = detector.detect_lanes(image)

# 중심 오프셋 계산
offset = detector.calculate_center_offset(lanes, image_width=320)

# 차선 그리기
result_image = detector.draw_lanes(image, lanes)
```

#### 알고리즘 흐름

1. 그레이스케일 변환
2. 가우시안 블러 (노이즈 제거)
3. Canny 엣지 검출
4. ROI(관심 영역) 마스크 적용
5. Hough 변환으로 직선 검출
6. 왼쪽/오른쪽 차선 분류

---

## 💡 사용 예시

### JavaScript에서 API 호출

```javascript
// 객체 감지
async function detectObjects() {
    const response = await fetch('/api/ai/detect');
    const data = await response.json();
    
    if (data.success) {
        console.log(`총 ${data.summary.total_objects}개 객체 감지됨`);
        data.objects.forEach(obj => {
            console.log(`- ${obj.label} (신뢰도: ${obj.confidence})`);
        });
    }
}

// 차선 감지
async function detectLanes() {
    const response = await fetch('/api/ai/lanes');
    const data = await response.json();
    
    if (data.success) {
        console.log(`${data.lanes.length}개 차선 감지됨`);
        console.log(`중심 오프셋: ${data.center_offset}px`);
    }
}

// 이미지로 결과 받기
function showDetectionImage() {
    const img = document.getElementById('result-img');
    img.src = '/api/ai/detect?draw=true&t=' + Date.now();
}
```

### Python에서 API 호출

```python
import requests

# 객체 감지
response = requests.get('http://localhost:5000/api/ai/detect')
data = response.json()

for obj in data['objects']:
    print(f"{obj['label']}: {obj['confidence']:.2f}")
    print(f"  위치: {obj['rect']}")

# 차선 감지
response = requests.get('http://localhost:5000/api/ai/lanes')
data = response.json()

print(f"감지된 차선: {len(data['lanes'])}개")
print(f"중심 오프셋: {data['center_offset']}px")
```

---

## 🎯 자율주행 응용

### 차선 유지 로직

```python
def decide_direction(center_offset):
    """
    차선 중심 오프셋을 기반으로 방향 결정
    
    Args:
        center_offset: 차선 중심 오프셋 (픽셀)
        
    Returns:
        "left", "right", "center"
    """
    THRESHOLD = 20  # 임계값 (픽셀)
    
    if center_offset is None:
        return "stop"  # 차선 감지 실패
    
    if center_offset < -THRESHOLD:
        return "left"  # 왼쪽으로 치우침 → 왼쪽으로 회전
    elif center_offset > THRESHOLD:
        return "right"  # 오른쪽으로 치우침 → 오른쪽으로 회전
    else:
        return "center"  # 중앙 유지
```

### 장애물 회피 로직

```python
def check_obstacles(detections, min_distance=100):
    """
    전방 장애물 확인
    
    Args:
        detections: YOLO 감지 결과
        min_distance: 최소 안전 거리 (픽셀)
        
    Returns:
        장애물 존재 여부
    """
    for obj in detections:
        # 중앙 하단에 위치한 객체 확인
        bbox = obj['bbox']
        center_x = bbox['x'] + bbox['width'] / 2
        bottom_y = bbox['y'] + bbox['height']
        
        # 이미지 중앙 하단 영역에 객체가 있으면 위험
        if 100 < center_x < 220 and bottom_y > 200:
            return True
    
    return False
```

---

## 🔍 YOLO 지원 클래스

YOLOv8n 모델은 **80개 클래스**를 감지할 수 있습니다:

### 주요 클래스 목록

- **사람**: person
- **차량**: bicycle, car, motorcycle, bus, truck
- **동물**: bird, cat, dog, horse, sheep, cow
- **교통**: traffic light, stop sign
- **기타**: chair, bottle, cup, laptop, cell phone 등

전체 목록은 [COCO Dataset](https://cocodataset.org/#explore)을 참고하세요.

---

## ⚙️ 성능 최적화

### 모델 선택

| 모델 | 크기 | 속도 | 정확도 |
|------|------|------|--------|
| yolov8n.pt | 6MB | 빠름 | 낮음 |
| yolov8s.pt | 22MB | 중간 | 중간 |
| yolov8m.pt | 52MB | 느림 | 높음 |
| yolov8l.pt | 87MB | 매우 느림 | 매우 높음 |

**권장**: ESP32-CAM의 저해상도 이미지에는 `yolov8n.pt`가 적합합니다.

### 신뢰도 임계값 조정

```python
# 낮은 임계값 (더 많은 객체 감지, 오탐 증가)
detector = YOLODetector(confidence_threshold=0.3)

# 높은 임계값 (신뢰도 높은 객체만 감지)
detector = YOLODetector(confidence_threshold=0.7)
```

---

## 🐛 트러블슈팅

### 1. YOLO 모델 로드 실패

**증상**: `YOLO 모델이 로드되지 않았습니다` 에러

**해결**:
```bash
# ultralytics 재설치
pip uninstall ultralytics
pip install ultralytics

# PyTorch 설치 확인
python -c "import torch; print(torch.__version__)"
```

### 2. OpenCV 이미지 디코딩 실패

**증상**: `이미지 디코딩 실패` 에러

**해결**:
- ESP32-CAM 연결 확인
- 이미지 형식이 JPEG인지 확인
- OpenCV 재설치: `pip install --upgrade opencv-python`

### 3. 메모리 부족

**증상**: 서버가 느려지거나 멈춤

**해결**:
- 더 가벼운 모델 사용 (yolov8n.pt)
- 이미지 해상도 낮추기
- 분석 빈도 줄이기

---

## 📚 참고 자료

- **Ultralytics YOLOv8**: https://docs.ultralytics.com/
- **OpenCV 문서**: https://docs.opencv.org/
- **COCO Dataset**: https://cocodataset.org/

---

**작성일**: 2025-10-22  
**버전**: 1.0.0  
**작성자**: ESP32-CAM Free Car Project Team

