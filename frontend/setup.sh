#!/bin/bash

# ESP32-CAM Flask 모니터링 시스템 설치 스크립트
# 사용법: bash setup.sh

echo "=================================================="
echo "ESP32-CAM Flask 모니터링 시스템 설치"
echo "=================================================="

# 현재 디렉토리 확인
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo "[1/4] Python 버전 확인..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python3가 설치되어 있지 않습니다."
    echo "Python 3.8 이상을 설치해주세요."
    exit 1
fi

echo ""
echo "[2/4] 가상환경 생성..."
if [ -d "venv" ]; then
    echo "⚠️  기존 가상환경이 존재합니다."
    read -p "삭제하고 다시 생성하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo "✅ 가상환경 재생성 완료"
    else
        echo "기존 가상환경 사용"
    fi
else
    python3 -m venv venv
    echo "✅ 가상환경 생성 완료"
fi

echo ""
echo "[3/4] 가상환경 활성화..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ 가상환경 활성화 실패"
    exit 1
fi

echo "✅ 가상환경 활성화 완료"

echo ""
echo "[4/4] 필요한 패키지 설치..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ 패키지 설치 실패"
    exit 1
fi

echo "✅ 패키지 설치 완료"

echo ""
echo "=================================================="
echo "설치 완료! 🎉"
echo "=================================================="
echo ""
echo "다음 명령으로 서버를 실행하세요:"
echo ""
echo "  cd $SCRIPT_DIR"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "또는 간단하게:"
echo ""
echo "  bash run.sh"
echo ""
echo "웹 브라우저에서 http://localhost:5000 접속"
echo "=================================================="






