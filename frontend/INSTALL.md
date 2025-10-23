# 설치 및 실행 가이드

ESP32-CAM Flask 모니터링 시스템의 설치 및 실행 방법입니다.

## 📋 사전 요구사항

- Python 3.8 이상
- pip (Python 패키지 관리자)
- ESP32-CAM이 WiFi에 연결되어 있어야 함

## 🚀 빠른 시작

### macOS / Linux

```bash
# 1. frontend 폴더로 이동
cd frontend

# 2. 자동 설치 스크립트 실행
bash setup.sh

# 3. 서버 실행
bash run.sh
```

### Windows

```batch
# 1. frontend 폴더로 이동
cd frontend

# 2. 자동 설치 스크립트 실행
setup.bat

# 3. 서버 실행
run.bat
```

## 📦 수동 설치

자동 스크립트를 사용하지 않는 경우:

### 1. 가상환경 생성

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 2. 패키지 설치

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. ESP32-CAM IP 설정

`app.py` 파일을 열어서 8번째 줄 수정:

```python
ESP32_IP = "192.168.0.65"  # 실제 ESP32-CAM IP로 변경
```

### 4. 서버 실행

```bash
python app.py
```

### 5. 브라우저에서 접속

```
http://localhost:5000
```

## 📚 설치된 패키지

`requirements.txt`에 포함된 패키지:

- **Flask 3.0.0**: 웹 프레임워크
- **requests 2.31.0**: HTTP 클라이언트 (ESP32와 통신)
- **Werkzeug 3.0.1**: WSGI 유틸리티 라이브러리

## 🔧 문제 해결

### Python을 찾을 수 없음

```bash
# Python 설치 확인
python3 --version

# 또는
python --version
```

Python이 설치되지 않았다면:
- macOS: `brew install python3`
- Windows: [python.org](https://www.python.org/downloads/)에서 다운로드
- Linux: `sudo apt install python3 python3-pip`

### 가상환경 활성화 실패

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows (Command Prompt):**
```batch
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

PowerShell 실행 정책 오류 시:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 패키지 설치 오류

```bash
# pip 업그레이드
pip install --upgrade pip

# 캐시 삭제 후 재설치
pip cache purge
pip install -r requirements.txt
```

### ESP32-CAM 연결 실패

1. ESP32-CAM 전원 확인
2. 같은 WiFi 네트워크 연결 확인
3. IP 주소 확인:
   ```bash
   ping 192.168.0.65
   ```
4. 방화벽 확인

### 포트 5000이 이미 사용 중

`app.py` 마지막 줄 수정:

```python
app.run(host='0.0.0.0', port=5001, debug=True)  # 다른 포트 사용
```

## 🛠️ 개발 모드

### 자동 재시작 활성화

Flask 디버그 모드가 기본으로 활성화되어 있어 코드 변경 시 자동 재시작됩니다.

### 환경 변수 설정

`.env` 파일 생성 (선택사항):

```env
FLASK_APP=app.py
FLASK_ENV=development
ESP32_IP=192.168.0.65
```

## 📝 가상환경 비활성화

작업이 끝나면:

```bash
deactivate
```

## 🔄 업데이트

패키지 업데이트:

```bash
# 가상환경 활성화 후
pip install --upgrade -r requirements.txt
```

## 🗑️ 제거

```bash
# 가상환경 삭제
rm -rf venv

# 또는 Windows
rmdir /s venv
```

## 📞 도움말

문제가 계속되면:
1. 로그 확인: 터미널/콘솔 출력 확인
2. 브라우저 개발자 도구 (F12) 확인
3. ESP32-CAM 시리얼 모니터 확인

## 🎯 다음 단계

설치가 완료되면 [README.md](README.md)에서 사용 방법을 확인하세요.









