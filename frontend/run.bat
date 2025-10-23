@echo off
REM ESP32-CAM Flask 모니터링 시스템 실행 스크립트 (Windows)
REM 사용법: run.bat

REM 가상환경 확인
if not exist venv (
    echo ❌ 가상환경이 없습니다.
    echo 먼저 setup.bat을 실행하세요.
    pause
    exit /b 1
)

echo ==================================================
echo ESP32-CAM Flask 모니터링 시스템 시작
echo ==================================================

REM 가상환경 활성화
echo 가상환경 활성화 중...
call venv\Scripts\activate.bat

REM Flask 서버 실행
echo Flask 서버 시작...
echo.
python app.py

pause








