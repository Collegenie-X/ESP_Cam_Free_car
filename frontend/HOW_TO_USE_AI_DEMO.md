# 🎯 AI 객체 감지 데모 사용 방법

## ✅ 준비 완료!

YOLO 모델이 성공적으로 다운로드되고 적용되었습니다!

---

## 🚀 바로 사용하기

### 1단계: 서버가 실행 중인지 확인

```bash
cd frontend
source venv/bin/activate
python app.py
```

### 2단계: 웹 브라우저 열기

다음 주소 중 하나로 접속하세요:

```
http://localhost:5001/ai-demo
```

또는

```
http://localhost:5002/ai-demo
```

(포트는 자동으로 선택됩니다)

---

## 📸 사용 방법

### 화면 구성

```
┌──────────────────────────────────────────────────────┐
│  🤖 ESP32-CAM AI 객체 감지 데모                       │
├──────────────────────────────────────────────────────┤
│  [🎯 객체 감지]  [🛣️ 차선 감지]  [🔍 종합 분석]     │
├─────────────────────┬────────────────────────────────┤
│  📹 분석 결과 이미지 │  📊 분석 결과                  │
│                     │                                │
│  [이미지 표시]       │  총 감지된 객체: 2개           │
│                     │                                │
│                     │  1. person                     │
│                     │     신뢰도: 92.0%              │
│                     │     Rect: (100,150)→(300,450)  │
│                     │                                │
│                     │  2. car                        │
│                     │     신뢰도: 85.0%              │
│                     │     Rect: (350,200)→(530,420)  │
└─────────────────────┴────────────────────────────────┘
```

### 버튼 기능

#### 🎯 객체 감지
- ESP32-CAM에서 현재 이미지 캡처
- YOLO 모델로 객체 감지
- 감지된 객체의 **Label**과 **Rect 좌표** 표시

**결과 예시:**
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

#### 🛣️ 차선 감지
- 도로 차선 인식
- 왼쪽/오른쪽 차선 위치 표시
- 중심 오프셋 계산 (자율주행용)

#### 🔍 종합 분석
- 객체 감지 + 차선 감지 동시 수행
- 모든 정보를 한 번에 표시

---

## 🎯 Rect 좌표 설명

### 좌표 시스템

```
(0,0) ───────────────────► X
 │
 │    (x1,y1) ┌──────────┐
 │            │          │
 │            │  객체    │
 │            │          │
 │            └──────────┘ (x2,y2)
 │
 ▼
 Y
```

### 반환되는 정보

1. **rect** (사각형 좌표)
   - `x1, y1`: 좌상단 좌표
   - `x2, y2`: 우하단 좌표

2. **bbox** (Bounding Box)
   - `x, y`: 시작 위치 (좌상단)
   - `width`: 가로 길이 (x2 - x1)
   - `height`: 세로 길이 (y2 - y1)

3. **label** (객체 이름)
   - 예: person, car, dog, cat 등

4. **confidence** (신뢰도)
   - 0.0 ~ 1.0 (0% ~ 100%)

---

## 💻 API로 직접 사용하기

### JavaScript 예시

```javascript
// 객체 감지
async function detectObjects() {
    const response = await fetch('/api/ai/detect');
    const data = await response.json();
    
    console.log(`총 ${data.summary.total_objects}개 객체 감지됨`);
    
    data.objects.forEach(obj => {
        console.log(`\n${obj.label}:`);
        console.log(`  신뢰도: ${(obj.confidence * 100).toFixed(1)}%`);
        console.log(`  Rect: (${obj.rect.x1}, ${obj.rect.y1}) → (${obj.rect.x2}, ${obj.rect.y2})`);
        console.log(`  크기: ${obj.bbox.width} x ${obj.bbox.height}`);
    });
}

detectObjects();
```

### Python 예시

```python
import requests

# 객체 감지
response = requests.get('http://localhost:5001/api/ai/detect')
data = response.json()

print(f"총 {data['summary']['total_objects']}개 객체 감지됨\n")

for i, obj in enumerate(data['objects'], 1):
    print(f"{i}. {obj['label']}")
    print(f"   신뢰도: {obj['confidence']:.2f}")
    print(f"   Rect: ({obj['rect']['x1']}, {obj['rect']['y1']}) → ({obj['rect']['x2']}, {obj['rect']['y2']})")
    print(f"   크기: {obj['bbox']['width']} x {obj['bbox']['height']}\n")
```

### curl 예시

```bash
# JSON 결과
curl http://localhost:5001/api/ai/detect

# 이미지 결과 (Bounding Box 표시)
curl http://localhost:5001/api/ai/detect?draw=true > result.jpg
open result.jpg  # Mac
```

---

## 🔥 실전 활용 예시

### 1. 장애물 감지 후 정지

```python
import requests

# 객체 감지
response = requests.get('http://localhost:5001/api/ai/detect')
data = response.json()

# 전방 중앙에 객체가 있는지 확인
for obj in data['objects']:
    center_x = (obj['rect']['x1'] + obj['rect']['x2']) / 2
    bottom_y = obj['rect']['y2']
    
    # 이미지 중앙 하단 (위험 구역)
    if 100 < center_x < 220 and bottom_y > 200:
        print(f"⚠️ 장애물 감지: {obj['label']}")
        # ESP32에 정지 명령
        requests.get('http://192.168.0.65/control?cmd=stop')
        break
```

### 2. 특정 객체 추적

```python
# 사람 찾기
response = requests.get('http://localhost:5001/api/ai/detect')
data = response.json()

people = [obj for obj in data['objects'] if obj['label'] == 'person']

if people:
    print(f"사람 {len(people)}명 감지됨")
    
    for person in people:
        x_center = (person['rect']['x1'] + person['rect']['x2']) / 2
        
        if x_center < 160:  # 이미지 중앙 기준 (320x240)
            print("→ 사람이 왼쪽에 있음")
            requests.get('http://192.168.0.65/control?cmd=left')
        else:
            print("← 사람이 오른쪽에 있음")
            requests.get('http://192.168.0.65/control?cmd=right')
```

### 3. 영역 기반 감지

```python
# 관심 영역 (ROI) 정의
danger_zone = {
    'x1': 80, 'y1': 150,
    'x2': 240, 'y2': 240
}

def is_in_zone(rect, zone):
    """객체가 영역 안에 있는지 확인"""
    obj_center_x = (rect['x1'] + rect['x2']) / 2
    obj_center_y = (rect['y1'] + rect['y2']) / 2
    
    return (zone['x1'] <= obj_center_x <= zone['x2'] and
            zone['y1'] <= obj_center_y <= zone['y2'])

# 감지
response = requests.get('http://localhost:5001/api/ai/detect')
data = response.json()

dangerous_objects = [
    obj for obj in data['objects']
    if is_in_zone(obj['rect'], danger_zone)
]

if dangerous_objects:
    print(f"⚠️ 위험 구역에 {len(dangerous_objects)}개 객체!")
    for obj in dangerous_objects:
        print(f"  - {obj['label']} (신뢰도: {obj['confidence']:.2f})")
```

---

## 🎨 지원하는 객체 클래스

### 교통 관련 (8개)
- person (사람)
- bicycle (자전거)
- car (자동차)
- motorcycle (오토바이)
- bus (버스)
- truck (트럭)
- traffic light (신호등)
- stop sign (정지 표지판)

### 동물 (6개)
- bird, cat, dog, horse, sheep, cow

### 생활용품 (다수)
- bottle, cup, chair, laptop, cell phone, book 등

**총 80개 클래스 지원** (COCO Dataset)

---

## 📊 성능 정보

### 처리 속도
- **CPU**: 1-3초/이미지
- **GPU**: 0.1-0.5초/이미지

### 모델 크기
- **yolov8n.pt**: 6.2 MB (현재 사용 중)

### 정확도
- 일반적인 객체: 70-95%
- 작은 객체: 50-70%

---

## 🔧 문제 해결

### Q: 객체가 감지되지 않아요
**A:** 
1. 조명을 밝게 하세요
2. 카메라 각도를 조정하세요
3. 객체가 화면 중앙에 오도록 하세요

### Q: 분석이 느려요
**A:** 정상입니다. CPU에서는 1-3초가 소요됩니다.

### Q: 엉뚱한 것이 감지돼요
**A:** 신뢰도(confidence)를 확인하세요. 70% 이상만 사용하는 것을 권장합니다.

---

## 📚 추가 리소스

- **상세 문서**: `AI_USAGE.md`
- **빠른 시작**: `AI_QUICK_START.md`
- **트러블슈팅**: `TROUBLESHOOTING.md`
- **데모 가이드**: `AI_DEMO_GUIDE.md`

---

## 🎉 요약

✅ YOLO 모델 다운로드 완료 (`yolov8n.pt`)  
✅ PyTorch 2.6+ 호환 문제 해결  
✅ 웹 데모 페이지 준비 완료  
✅ API 사용 가능  

**이제 바로 사용하세요!**

```
웹 브라우저에서:
http://localhost:5001/ai-demo
```

---

**Happy Object Detection! 🤖📸**

