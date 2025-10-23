#!/bin/bash

# 캡처 속도 테스트 스크립트
# 사용법: ./test_capture_speed.sh [ESP32_IP]

ESP32_IP=${1:-192.168.0.65}
CAPTURE_URL="http://${ESP32_IP}/capture"
TEST_COUNT=50

# test_images 폴더 생성 (없으면)
mkdir -p ./test_images

echo "======================================"
echo "📸 ESP32-CAM 캡처 속도 테스트"
echo "======================================"
echo "ESP32 주소: ${ESP32_IP}"
echo "테스트 횟수: ${TEST_COUNT}회"
echo "저장 경로: ./test_images/"
echo "======================================"
echo ""

# 이전 테스트 이미지 정리 (선택사항)
if [ "$(ls -A ./test_images 2>/dev/null)" ]; then
    echo "⚠️  이전 테스트 이미지가 있습니다."
    read -p "삭제하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f ./test_images/test_capture_*.jpg
        echo "✅ 이전 이미지 삭제 완료"
    fi
    echo ""
fi

# 테스트 시작
total_time=0
success_count=0

for i in $(seq 1 $TEST_COUNT); do
    echo -n "[$i/$TEST_COUNT] 캡처 중... "
    
    # 시간 측정 (밀리초)
    start=$(python3 -c 'import time; print(int(time.time() * 1000))')
    
    # ✅ 최적화된 캡처 요청
    output_file="test_images/test_capture_$i.jpg"
    
    # 파일 저장 전 디렉토리 확인
    mkdir -p "$(dirname "$output_file")"
    
    http_code=$(curl -v \
        -o "$output_file" \
        -w "%{http_code}" \
        --max-time 2 \
        -H "Connection: keep-alive" \
        -H "Accept: image/jpeg" \
        --keepalive-time 5 \
        --compressed \
        "${CAPTURE_URL}" 2>curl_debug.log)
    
    end=$(python3 -c 'import time; print(int(time.time() * 1000))')
    elapsed=$((end - start))
    
    if [ "$http_code" = "200" ] && [ -f "$output_file" ]; then
        file_size=$(ls -lh "$output_file" | awk '{print $5}')
        echo "✅ ${elapsed}ms (${file_size})"
        total_time=$((total_time + elapsed))
        success_count=$((success_count + 1))
    else
        echo "❌ 실패 (HTTP ${http_code})"
        # 실패한 파일 삭제
        rm -f "$output_file" 2>/dev/null
    fi
    
    # ✅ 더 짧은 대기 (3FPS 목표)
    sleep 0.05
done

echo ""
echo "======================================"
echo "📊 테스트 결과"
echo "======================================"
echo "성공: ${success_count}/${TEST_COUNT}회"

if [ $success_count -gt 0 ]; then
    avg_time=$((total_time / success_count))
    max_fps=$((1000 / avg_time))
    
    echo "평균 캡처 시간: ${avg_time}ms"
    echo "예상 최대 FPS: ~${max_fps} FPS"
    echo ""
    
    # 성능 평가
    if [ $avg_time -lt 100 ]; then
        echo "🎉 우수: 실시간 자율주행 가능! (10+ FPS)"
    elif [ $avg_time -lt 150 ]; then
        echo "✅ 양호: 자율주행 가능 (7-10 FPS)"
    elif [ $avg_time -lt 200 ]; then
        echo "⚠️  보통: 자율주행 가능하나 느림 (5-7 FPS)"
    else
        echo "❌ 느림: 최적화 필요 (5 FPS 미만)"
    fi
else
    echo "❌ 모든 테스트 실패"
    echo "ESP32-CAM 연결을 확인하세요."
fi

echo "======================================"

# 저장된 이미지 정보
if [ $success_count -gt 0 ]; then
    echo ""
    echo "💾 저장된 이미지:"
    echo "   위치: test_images/"
    echo "   파일: test_capture_1.jpg ~ test_capture_${success_count}.jpg"
    echo ""
    
    # 이미지 확인 (macOS)
    first_image="test_images/test_capture_1.jpg"
    if [ -f "$first_image" ]; then
        echo "✅ 이미지 열기..."
        open "$first_image"
    else
        echo "⚠️  이미지 파일이 없습니다."
        ls -l test_images/  # 디버깅용 디렉토리 내용 출력
    fi
fi

