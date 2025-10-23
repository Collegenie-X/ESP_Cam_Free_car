@echo off
REM ESP32-CAM Flask 모니터링 시스템 설치 스크립트 (Windows)
REM 사용법: setup.bat

echo ==================================================
echo ESP32-CAM Flask 모니터링 시스템 설치
echo ==================================================

echo.
echo [1/4] Python 버전 확인...
python --version

if errorlevel 1 (
    echo ❌ Python이 설치되어 있지 않습니다.
    echo Python 3.8 이상을 설치해주세요.
    pause
    exit /b 1
)

echo.
echo [2/4] 가상환경 생성...
if exist venv (
    echo ⚠️  기존 가상환경이 존재합니다.
    set /p REPLY="삭제하고 다시 생성하시겠습니까? (y/N): "
    if /i "%REPLY%"=="y" (
        rmdir /s /q venv
        python -m venv venv
        echo ✅ 가상환경 재생성 완료
    ) else (
        echo 기존 가상환경 사용
    )
) else (
    python -m venv venv
    echo ✅ 가상환경 생성 완료
)

echo.
echo [3/4] 가상환경 활성화...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo ❌ 가상환경 활성화 실패
    pause
    exit /b 1
)

echo ✅ 가상환경 활성화 완료

echo.
echo [4/4] 필요한 패키지 설치...
python -m pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ 패키지 설치 실패
    pause
    exit /b 1
)

echo ✅ 패키지 설치 완료

echo.
echo ==================================================
echo 설치 완료! 🎉
echo ==================================================
echo.
echo 다음 명령으로 서버를 실행하세요:
echo.
echo   venv\Scripts\activate
echo   python app.py
echo.
echo 또는 간단하게:
echo.
echo   run.bat
echo.
echo 웹 브라우저에서 http://localhost:5000 접속
echo ==================================================
echo.
pause










