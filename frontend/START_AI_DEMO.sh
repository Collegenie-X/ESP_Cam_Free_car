#!/bin/bash

# ESP32-CAM AI 객체 감지 데모 시작 스크립트

echo "========================================================"
echo "🤖 ESP32-CAM AI 객체 감지 데모"
echo "========================================================"
echo ""

# 현재 디렉토리 확인
if [ ! -f "app.py" ]; then
    echo "❌ 오류: frontend 폴더에서 실행해주세요"
    echo "   cd frontend"
    echo "   ./START_AI_DEMO.sh"
    exit 1
fi

echo "1️⃣ 가상환경 활성화..."
source venv/bin/activate

echo "2️⃣ YOLO 모델 확인..."
if [ -f "yolov8n.pt" ]; then
    echo "✅ YOLO 모델 파일 존재: yolov8n.pt"
else
    echo "⚠️  YOLO 모델 파일이 없습니다. 첫 실행 시 자동으로 다운로드됩니다."
fi

echo ""
echo "3️⃣ 서버 시작 중..."
echo ""

# 서버 실행
python3 app.py

# 또는 백그라운드 실행:
# nohup python3 app.py > server.log 2>&1 &
# echo "✅ 서버가 백그라운드에서 시작되었습니다"
# echo ""
# echo "로그 확인: tail -f server.log"
# echo "서버 종료: pkill -f 'python3 app.py'"

