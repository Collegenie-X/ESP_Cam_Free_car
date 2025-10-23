import cv2
import time
import requests
import numpy as np

URL = "http://192.168.0.65/stream"

# 트랙바 설정
cv2.namedWindow("Edges | Left: Color  Right: Canny")
cv2.createTrackbar("Low", "Edges | Left: Color  Right: Canny", 50, 255, lambda v: None)
cv2.createTrackbar(
    "High", "Edges | Left: Color  Right: Canny", 150, 255, lambda v: None
)

print("[INFO] 스트림 연결 중...")
print("[INFO] q 키로 종료")

try:
    with requests.get(URL, stream=True, timeout=10) as r:
        if not r.ok:
            raise RuntimeError(
                f"스트림 연결 실패 (HTTP {r.status_code}). URL을 확인하세요."
            )

        print("[INFO] 연결 성공!")
        byte_buffer = b""
        prev = time.time()
        cnt = 0
        fps = 0
        resize_ratio = None  # 첫 프레임에서 계산

        for chunk in r.iter_content(chunk_size=4096):
            if not chunk:
                continue

            byte_buffer += chunk

            # 버퍼가 너무 크면 리셋 (메모리 보호)
            if len(byte_buffer) > 10 * 1024 * 1024:  # 10MB
                print("[WARN] 버퍼 리셋")
                byte_buffer = byte_buffer[-4096:]
                continue

            # JPEG 프레임 찾기
            a = byte_buffer.find(b"\xff\xd8")  # JPEG 시작
            b = byte_buffer.find(b"\xff\xd9")  # JPEG 끝

            if a != -1 and b != -1 and b > a:
                jpg_data = byte_buffer[a : b + 2]
                byte_buffer = byte_buffer[b + 2 :]

                # 프레임 디코딩
                frame = cv2.imdecode(
                    np.frombuffer(jpg_data, dtype=np.uint8), cv2.IMREAD_COLOR
                )
                if frame is None:
                    continue

                # 그레이스케일 및 블러
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                blur = cv2.GaussianBlur(gray, (5, 5), 1.4)

                # 트랙바 값으로 Canny
                low = cv2.getTrackbarPos("Low", "Edges | Left: Color  Right: Canny")
                high = cv2.getTrackbarPos("High", "Edges | Left: Color  Right: Canny")
                edges = cv2.Canny(blur, low, high)
                edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

                # 리사이즈 비율 계산 (첫 프레임만)
                if resize_ratio is None:
                    max_w = 640
                    resize_ratio = min(1.0, max_w / frame.shape[1])

                # 리사이즈 적용
                if resize_ratio < 1.0:
                    new_w = int(frame.shape[1] * resize_ratio)
                    new_h = int(frame.shape[0] * resize_ratio)
                    frame = cv2.resize(frame, (new_w, new_h))
                    edges_bgr = cv2.resize(edges_bgr, (new_w, new_h))

                # FPS 계산
                cnt += 1
                now = time.time()
                if now - prev >= 1:
                    fps = cnt
                    cnt = 0
                    prev = now

                # 텍스트 추가
                cv2.putText(
                    frame,
                    f"Color | FPS {fps}",
                    (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )
                cv2.putText(
                    edges_bgr,
                    f"Canny (L:{low} H:{high})",
                    (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2,
                )

                # 좌우 결합 출력
                both = cv2.hconcat([frame, edges_bgr])
                cv2.imshow("Edges | Left: Color  Right: Canny", both)

                # q 키로 종료
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

except requests.exceptions.Timeout:
    print("[ERROR] 연결 시간 초과. URL과 네트워크를 확인하세요.")
except requests.exceptions.RequestException as e:
    print(f"[ERROR] 네트워크 오류: {e}")
except KeyboardInterrupt:
    print("\n[INFO] 사용자 중단")
finally:
    cv2.destroyAllWindows()
    print("[INFO] 종료")
