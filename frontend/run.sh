#!/bin/bash

# ESP32-CAM Flask 모니터링 시스템 실행 스크립트
# 사용법: bash run.sh

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo "❌ 가상환경이 없습니다."
    echo "먼저 setup.sh를 실행하세요: bash setup.sh"
    exit 1
fi

echo "=================================================="
echo "ESP32-CAM Flask 모니터링 시스템 시작"
echo "=================================================="

# 가상환경 활성화
echo "가상환경 활성화 중..."
source venv/bin/activate

# Flask 서버 실행
echo "Flask 서버 시작..."
echo ""
python app.py








