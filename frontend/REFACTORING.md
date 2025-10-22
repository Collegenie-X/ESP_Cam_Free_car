# 프론트엔드 리팩토링 문서

## 🎯 리팩토링 목표

기존 단일 파일(`app.py`)로 구성된 Flask 애플리케이션을 **모듈화**하여 유지보수성과 확장성을 향상시킵니다.

---

## 📁 변경된 폴더 구조

### Before (기존)
```
frontend/
├── app.py                    # 모든 로직이 하나의 파일에 집중
├── config.py
└── templates/
    └── index.html
```

### After (개선)
```
frontend/
├── app.py                    # 메인 진입점 (간소화됨)
├── config.py                 # 설정 파일 (변경 없음)
│
├── core/                     # 🔧 핵심 설정
│   ├── __init__.py
│   ├── app_factory.py        # Flask 앱 팩토리 (앱 생성 및 초기화)
│   └── logger_config.py      # 로거 설정
│
├── services/                 # 💼 비즈니스 로직
│   ├── __init__.py
│   └── esp32_communication_service.py  # ESP32 통신 서비스
│
├── routes/                   # 🛣️ 라우트 핸들러
│   ├── __init__.py
│   ├── main_routes.py        # 메인 페이지 라우트
│   ├── api_routes.py         # API 엔드포인트 라우트
│   └── camera_routes.py      # 카메라 관련 라우트
│
├── utils/                    # 🔨 유틸리티
│   ├── __init__.py
│   └── server_port_selector.py
│
└── templates/
    └── index.html
```

---

## 📦 모듈 설명

### 1. `core/` - 핵심 설정

#### `app_factory.py` - Flask 앱 팩토리
- **역할**: Flask 앱 생성 및 초기화
- **주요 함수**:
  - `create_app()`: 앱 생성 (팩토리 패턴)
  - `register_blueprints()`: 블루프린트 등록
  - `register_error_handlers()`: 에러 핸들러 등록

#### `logger_config.py` - 로거 설정
- **역할**: 애플리케이션 전체의 로깅 설정
- **주요 함수**:
  - `setup_logger()`: 로거 초기화

---

### 2. `services/` - 비즈니스 로직

#### `esp32_communication_service.py` - ESP32 통신 서비스
- **역할**: ESP32-CAM과의 HTTP 통신 담당
- **클래스**: `ESP32CommunicationService`
- **주요 메서드**:
  - `get_status()`: ESP32 상태 조회
  - `send_command()`: ESP32에 명령 전송
  - `get_stream_url()`: 스트림 URL 반환
  - `get_capture_url()`: 캡처 URL 반환

---

### 3. `routes/` - 라우트 핸들러

#### `main_routes.py` - 메인 페이지 라우트
- **역할**: 웹 페이지 렌더링
- **블루프린트**: `main_bp`
- **엔드포인트**:
  - `GET /`: 메인 대시보드
  - `GET /settings`: 설정 페이지

#### `api_routes.py` - API 엔드포인트 라우트
- **역할**: ESP32 제어 API
- **블루프린트**: `api_bp` (prefix: `/api`)
- **엔드포인트**:
  - `GET /api/status`: 상태 조회
  - `GET /api/control/<command>`: 모터 제어
  - `GET /api/led/<state>`: LED 제어
  - `GET /api/speed/<operation>`: 속도 제어
  - `GET /api/camera/<param>`: 카메라 설정

#### `camera_routes.py` - 카메라 관련 라우트
- **역할**: 카메라 이미지/스트림 제공
- **블루프린트**: `camera_bp`
- **엔드포인트**:
  - `GET /capture`: 단일 이미지 캡처
  - `GET /stream`: 비디오 스트리밍

---

## 🔄 주요 변경 사항

### 1. 팩토리 패턴 도입
```python
# Before
app = Flask(__name__)

# After
from core.app_factory import create_app
app = create_app()
```

### 2. 블루프린트로 라우트 그룹화
```python
# Before
@app.route("/")
def index():
    ...

# After
from flask import Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    ...
```

### 3. 서비스 계층 분리
```python
# Before
def send_esp32_command(endpoint, params=None):
    try:
        url = f"{ESP32_BASE_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        ...

# After
class ESP32CommunicationService:
    def send_command(self, endpoint, params=None):
        ...
```

---

## ✅ 장점

### 1. **관심사의 분리 (Separation of Concerns)**
- UI 로직 (`routes/`)과 비즈니스 로직 (`services/`) 분리
- 각 모듈이 명확한 책임을 가짐

### 2. **재사용성 향상**
- `ESP32CommunicationService`는 다른 프로젝트에서도 사용 가능
- 독립적인 모듈로 테스트 용이

### 3. **확장성 증대**
- 새로운 기능 추가 시 해당 폴더에 파일만 추가
- 예: 새로운 API → `routes/` 폴더에 블루프린트 추가

### 4. **유지보수 편리**
- 기능별로 파일이 분리되어 코드 찾기 쉬움
- 버그 수정 시 영향 범위가 명확함

### 5. **가독성 향상**
- `app.py`가 237줄 → 38줄로 감소
- 파일명만으로 기능 파악 가능

---

## 🚀 실행 방법

### 기존과 동일
```bash
# 가상환경 활성화
source venv/bin/activate  # Linux/Mac
# 또는
.\venv\Scripts\activate   # Windows

# 실행
python app.py
```

### 변경 사항 없음
- 사용자 입장에서는 동일하게 작동
- 내부 구조만 개선됨

---

## 📝 파일명 규칙

### 파일명 패턴
- **서비스**: `{기능}_service.py`
  - 예: `esp32_communication_service.py`
- **라우트**: `{기능}_routes.py`
  - 예: `main_routes.py`, `api_routes.py`
- **설정**: `{기능}_config.py`
  - 예: `logger_config.py`

### 함수명/클래스명 규칙
- **클래스명**: PascalCase (예: `ESP32CommunicationService`)
- **함수명**: snake_case (예: `get_status`, `send_command`)
- **상수명**: UPPER_SNAKE_CASE (예: `DEFAULT_ESP32_IP`)

---

## 🔍 디버깅 가이드

### 로그 확인
```python
# 로거는 모든 모듈에서 사용 가능
import logging
logger = logging.getLogger(__name__)

logger.info("정보 로그")
logger.error("에러 로그")
```

### 특정 기능 문제 발생 시

| 문제 영역 | 확인할 파일 |
|----------|-----------|
| 모터 제어 안됨 | `routes/api_routes.py` → `control_motor()` |
| 카메라 이미지 안나옴 | `routes/camera_routes.py` → `capture_image()` |
| ESP32 통신 실패 | `services/esp32_communication_service.py` |
| 페이지 렌더링 오류 | `routes/main_routes.py` |

---

## 📚 추가 참고

### Flask 블루프린트
- 공식 문서: https://flask.palletsprojects.com/en/latest/blueprints/
- 라우트를 모듈화하여 관리하는 Flask의 기능

### 팩토리 패턴
- 앱 생성 로직을 함수로 분리
- 테스트, 다중 인스턴스 생성 시 유리

---

## 🎓 학습 포인트

1. **모듈화의 중요성**: 큰 파일을 작은 단위로 분리
2. **디자인 패턴 활용**: 팩토리 패턴, 서비스 패턴
3. **클린 코드**: Early Return, 명확한 네이밍
4. **확장 가능한 구조**: 새 기능 추가가 쉬운 구조

---

## ⚠️ 주의사항

### 블루프린트 사용 시
- `current_app`으로 앱 설정에 접근
- 순환 참조(Circular Import) 주의

### 서비스 인스턴스
- `app.config`에 서비스 인스턴스 저장
- 라우트에서 `current_app.config.get()`으로 접근

---

**작성일**: 2025-10-22  
**버전**: 2.0.0  
**작성자**: ESP32-CAM Free Car Project Team

