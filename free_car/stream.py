import cv2

# 1) ESP32-CAM 스트림 주소 (본인 보드 IP로 교체)
URL = "http://192.168.0.65/stream"

# 2) 스트림 열기
cap = cv2.VideoCapture(URL)

# ✅ 버퍼 크기를 1로 설정하여 최신 프레임만 가져오기 (지연 해결)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not cap.isOpened():
    raise RuntimeError(
        "스트림을 열 수 없습니다.\n"
        "👉 브라우저에서 URL (예: http://192.168.0.65/stream) 이 열리는지 먼저 확인하세요."
    )

print("[INFO] 스트림 시작 - 'q' 키를 누르면 종료됩니다.")
print("[INFO] 버퍼 최적화 적용: 최신 프레임만 처리")

frame_count = 0
skip_count = 0

while True:
    ok, frame = cap.read()
    if not ok:
        print("⚠️ 프레임을 불러오지 못했습니다. 연결 상태를 확인하세요.")
        skip_count += 1
        # ✅ 연속으로 10번 실패하면 종료 (일시적 끊김은 무시)
        if skip_count > 10:
            print("❌ 스트림 연결이 끊어졌습니다.")
            break
        continue

    skip_count = 0  # 성공하면 카운트 리셋
    frame_count += 1

    # 3) 그레이스케일 변환 (BGR → GRAY)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 4) 화면에 나란히 표시하기 위해 GRAY → BGR 변환
    gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    # (선택) 크기 조절: 화면 해상도가 너무 크면 줄이기
    h, w = frame.shape[:2]
    if w > 640:
        scale = 640 / w
        # ✅ 보간법을 INTER_NEAREST로 변경하여 처리 속도 향상
        frame = cv2.resize(
            frame, (640, int(h * scale)), interpolation=cv2.INTER_NEAREST
        )
        gray_bgr = cv2.resize(
            gray_bgr, (640, int(h * scale)), interpolation=cv2.INTER_NEAREST
        )

    # 5) 좌우 병합 (컬러 | 흑백)
    both = cv2.hconcat([frame, gray_bgr])

    # ✅ FPS 정보 표시 (100프레임마다)
    if frame_count % 100 == 0:
        print(f"[INFO] 처리된 프레임: {frame_count}")

    # 6) 결과 출력
    cv2.imshow("ESP32-CAM | Left: Color  Right: Gray", both)

    # 7) 'q' 키로 종료
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    # ✅ 'r' 키로 스트림 재연결
    elif key == ord("r"):
        print("[INFO] 스트림 재연결 중...")
        cap.release()
        cap = cv2.VideoCapture(URL)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        print("[INFO] 재연결 완료")

# 8) 자원 해제
cap.release()
cv2.destroyAllWindows()
