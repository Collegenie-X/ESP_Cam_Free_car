# AI 기능 빠른 시작 가이드 🚀

## 1️⃣ 설치 (1분)

```bash
cd frontend
source venv/bin/activate  # 가상환경 활성화
pip install -r requirements.txt  # AI 패키지 설치
```

## 2️⃣ 서버 실행

```bash
python app.py
```

## 3️⃣ API 테스트

### 객체 감지
```bash
# JSON 결과
curl http://localhost:5000/api/ai/detect

# 이미지 결과 (Bounding Box 표시)
curl http://localhost:5000/api/ai/detect?draw=true > result.jpg
```

### 차선 감지
```bash
# JSON 결과
curl http://localhost:5000/api/ai/lanes

# 이미지 결과 (차선 표시)
curl http://localhost:5000/api/ai/lanes?draw=true > lanes.jpg
```

### 종합 분석 (객체 + 차선)
```bash
# JSON 결과
curl http://localhost:5000/api/ai/analyze

# 이미지 결과
curl http://localhost:5000/api/ai/analyze?draw=true > full.jpg
```

## 4️⃣ 결과 해석

### 객체 감지 결과
```json
{
  "label": "person",        // 객체 종류
  "confidence": 0.92,       // 신뢰도 (0~1)
  "bbox": {                 // Bounding Box
    "x": 100,              // 좌상단 X
    "y": 150,              // 좌상단 Y
    "width": 200,          // 너비
    "height": 300          // 높이
  },
  "rect": {                 // 사각형 좌표
    "x1": 100, "y1": 150,  // 좌상단
    "x2": 300, "y2": 450   // 우하단
  }
}
```

### 차선 감지 결과
```json
{
  "lanes": [
    {
      "side": "left",      // 왼쪽 차선
      "line": {            // 직선 좌표
        "x1": 100, "y1": 400,  // 시작점
        "x2": 200, "y2": 300   // 끝점
      }
    }
  ],
  "center_offset": 15      // 중심 오프셋 (픽셀)
}
```

## 5️⃣ 자율주행 응용

```python
# 차선 유지 로직
offset = data['center_offset']

if offset < -20:
    command = "left"   # 왼쪽으로 회전
elif offset > 20:
    command = "right"  # 오른쪽으로 회전
else:
    command = "center" # 직진
```

## 📚 상세 문서

- **전체 가이드**: [AI_USAGE.md](AI_USAGE.md)
- **리팩토링 문서**: [REFACTORING.md](REFACTORING.md)

---

**문의사항은 이슈로 등록해주세요!** 🙌

