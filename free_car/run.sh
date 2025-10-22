#!/bin/bash
# ESP32-CAM 자율주행차 실행 스크립트 (Mac/Linux)

echo "🚗 ESP32-CAM 자율주행차 시스템"
echo "================================"

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo "📦 가상환경이 없습니다. 생성 중..."
    python3 -m venv venv
fi

# 가상환경 활성화
echo "🔧 가상환경 활성화..."
source venv/bin/activate

# 라이브러리 설치/업데이트
echo "📚 라이브러리 확인..."
pip install -q -r requirements.txt

# .env 파일 확인
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다."
    if [ -f ".env.example" ]; then
        echo "📋 .env.example을 복사합니다..."
        cp .env.example .env
        echo "✅ .env 파일을 열어 ESP32_IP를 수정하세요."
    fi
fi

# 실행
echo ""
echo "🚀 자율주행 시작..."
echo ""
python main.py

