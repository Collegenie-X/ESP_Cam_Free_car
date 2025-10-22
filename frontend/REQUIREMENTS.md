# 📦 라이브러리 요구사항

이 문서는 ESP32-CAM 자율주행 시스템에 필요한 Python 라이브러리와 설치 방법을 설명합니다.

## 🔧 필수 라이브러리

### 1. Flask 웹 프레임워크
- **Flask (3.0.0)**: 웹 서버 및 API
- **Werkzeug (3.0.1)**: WSGI 유틸리티
- **requests (2.31.0)**: HTTP 클라이언트
- **blinker (1.9.0)**: Flask 시그널
- **Jinja2 (3.1.6)**: HTML 템플릿
- **MarkupSafe (3.0.3)**: HTML 이스케이핑

### 2. AI 및 이미지 처리
- **opencv-python (4.8.1.78)**: OpenCV 이미지 처리
  - CLAHE 전처리
  - HSV 색상 변환
  - 컨투어 검출
  - 히스토그램 분석
- **numpy (>=1.26)**: 배열 연산
  - 이미지 처리
  - 히스토그램 계산
- **ultralytics (8.0.196)**: YOLOv8 객체 감지
- **torch (>=2.0.0)**: PyTorch (YOLO 의존성)
- **torchvision (>=0.15.0)**: PyTorch Vision
- **Pillow (>=10.0.0)**: 이미지 처리

### 3. 유틸리티
- **python-dotenv (1.0.0)**: 환경변수 관리
- **typing-extensions (>=4.8.0)**: 타입 힌트
- **certifi (>=2025.10.5)**: HTTPS 인증서
- **charset-normalizer (>=3.4.0)**: 인코딩 처리
- **urllib3 (>=2.5.0)**: HTTP 클라이언트

## 🔨 개발 도구 (선택적)

### 1. 코드 품질
- **black (23.10.1)**: 코드 포맷터
- **isort (5.12.0)**: import 정렬
- **flake8 (6.1.0)**: 린터
- **mypy (1.6.1)**: 타입 체커

### 2. 테스트
- **pytest (7.4.3)**: 테스트 프레임워크

## 📥 설치 방법

### 1. 가상환경 생성 (권장)

```bash
# Python 3.13 이상 권장
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. 라이브러리 설치

```bash
# 필수 라이브러리만 설치
pip install -r requirements.txt

# 개발 도구 포함 설치 (선택적)
pip install -r requirements.txt[dev]
```

### 3. CUDA 지원 (선택적)

GPU 가속을 위한 CUDA 지원이 필요한 경우:

```bash
# CUDA 11.8 기준
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

## 🔍 버전 호환성

- **Python**: 3.13 이상 권장
- **CUDA**: 11.8 이상 (GPU 사용 시)
- **OpenCV**: 4.8 이상
- **PyTorch**: 2.0 이상

## ⚠️ 주의사항

1. **메모리 사용량**
   - YOLOv8 모델: ~2GB RAM
   - OpenCV 처리: ~500MB RAM
   - 최소 4GB RAM 권장

2. **저장 공간**
   - 전체 설치 크기: ~5GB
   - YOLOv8 모델: ~100MB
   - 가상환경: ~2GB

3. **성능 고려사항**
   - CPU: 멀티코어 권장
   - GPU: CUDA 지원 시 성능 향상
   - 네트워크: 최소 10Mbps 권장

## 🔄 업데이트 방법

```bash
# 최신 버전으로 업데이트
pip install -r requirements.txt --upgrade

# 특정 라이브러리만 업데이트
pip install -U opencv-python numpy
```

## 🐛 문제 해결

### 1. OpenCV 설치 오류
```bash
# macOS
brew install opencv

# Ubuntu
sudo apt-get install python3-opencv
```

### 2. PyTorch CUDA 오류
```bash
# CUDA 버전 확인
nvidia-smi

# PyTorch 재설치
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### 3. 메모리 부족
- YOLOv8n (작은 모델) 사용
- 이미지 크기 축소 (320x240)
- 배치 처리 비활성화

## 📚 참고 문서

- [Flask 문서](https://flask.palletsprojects.com/)
- [OpenCV 문서](https://docs.opencv.org/)
- [YOLOv8 문서](https://docs.ultralytics.com/)
- [PyTorch 문서](https://pytorch.org/docs/)
