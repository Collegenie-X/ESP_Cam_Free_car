import cv2
import numpy as np
import time

# 1) ESP32-CAM 스트림 주소
URL = "http://192.168.0.65/stream"  # ← 본인 IP로 변경
cap = cv2.VideoCapture(URL)
if not cap.isOpened():
    raise RuntimeError("스트림을 열 수 없습니다. 브라우저에서 URL 확인")

WIN = "COLOR TRACK | Left: ORIGINAL  Right: RESULT"
cv2.namedWindow(WIN)

kernel = np.ones((5, 5), np.uint8)
max_w = 640
prev, cnt, fps = time.time(), 0, 0

# ----- 기본 HSV 임계값 (GREEN) -----
Hc = 60  # 색상 중심 (Hue)
Rg = 15  # Hue ± 범위
S_min = 120  # 채도 하한
V_min = 80  # 명도 하한

print("[INFO] 키: r=RED, g=GREEN, b=BLUE, q=종료")

while True:
    ok, frame = cap.read()
    if not ok:
        continue

    # 보기 부담 줄이기
    if frame.shape[1] > max_w:
        r = max_w / frame.shape[1]
        frame = cv2.resize(
            frame, (max_w, int(frame.shape[0] * r)), interpolation=cv2.INTER_AREA
        )

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 2) Hue 랩어라운드 처리 (중심±범위)
    lowH = (Hc - Rg) % 180
    highH = (Hc + Rg) % 180
    if lowH <= highH:
        ranges = [(np.array([lowH, S_min, V_min]), np.array([highH, 255, 255]))]
    else:
        # 경계(0/179) 넘어가면 두 구간으로 분리
        ranges = [
            (np.array([0, S_min, V_min]), np.array([highH, 255, 255])),
            (np.array([lowH, S_min, V_min]), np.array([179, 255, 255])),
        ]

    # 3) 마스크 생성
    mask_total = None
    for lo, hi in ranges:
        m = cv2.inRange(hsv, lo, hi)
        mask_total = m if mask_total is None else cv2.bitwise_or(mask_total, m)

    # 노이즈 정리
    mask = cv2.morphologyEx(mask_total, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=1)

    # 4) 윤곽 & 가장 큰 영역 선택
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result = frame.copy()
    if cnts:
        c = max(cnts, key=cv2.contourArea)
        area = cv2.contourArea(c)
        if area > 500:  # 너무 작은 노이즈 제외
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 255), 2)

    # 5) 좌: 원본 | 우: 결과
    both = cv2.hconcat([frame, result])

    # FPS
    cnt += 1
    now = time.time()
    if now - prev >= 1:
        fps = cnt
        cnt = 0
        prev = now

    # 라벨
    cv2.putText(
        both, "ORIGINAL", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (50, 220, 50), 2
    )
    cv2.putText(
        both,
        f"RESULT  | FPS {fps}",
        (frame.shape[1] + 10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (50, 220, 50),
        2,
    )

    cv2.imshow(WIN, both)

    # 6) 프리셋 키: r/g/b
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("r"):  # RED
        Hc, Rg, S_min, V_min = 0, 15, 120, 80
        print("▶ RED MODE")
    elif key == ord("g"):  # GREEN
        Hc, Rg, S_min, V_min = 60, 15, 120, 80
        print("▶ GREEN MODE")
    elif key == ord("b"):  # BLUE
        Hc, Rg, S_min, V_min = 110, 15, 120, 80
        print("▶ BLUE MODE")

cap.release()
cv2.destroyAllWindows()
