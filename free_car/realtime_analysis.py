#!/usr/bin/env python3
"""
실시간 자율주행 분석 도구

/capture를 사용하여 1초당 3 프레임을 분석하고
원본 이미지와 분석 결과를 동시에 표시합니다.
"""

import cv2
import time
import requests
import numpy as np
from typing import Dict, Any, Tuple

# ESP32-CAM 설정
ESP32_IP = "192.168.0.65"
CAPTURE_URL = f"http://{ESP32_IP}/capture"
TARGET_FPS = 3  # 1초당 3 프레임

# 윈도우 이름
WINDOW_NAME = "자율주행 분석 | 왼쪽: 원본  오른쪽: 분석 결과"


class RealtimeAnalyzer:
    """실시간 분석 클래스"""

    def __init__(self):
        """초기화"""
        # 세션 생성 (연결 재사용)
        self.session = requests.Session()
        self.session.headers.update(
            {"Connection": "keep-alive", "Keep-Alive": "timeout=5, max=100"}
        )

        # HSV 범위 (트랙바로 조정 가능)
        self.hsv_params = {
            "white_v_min": 200,  # 흰색 V 최소값
            "white_s_max": 30,  # 흰색 S 최대값
            "brightness": 80,  # 밝기 임계값
            "min_pixels": 200,  # 최소 픽셀 수
        }

        # 통계
        self.stats = {
            "frames": 0,
            "errors": 0,
            "start_time": time.time(),
        }

        # CLAHE 초기화
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    def create_trackbars(self):
        """트랙바 생성"""
        cv2.namedWindow(WINDOW_NAME)

        # HSV 범위 조정
        cv2.createTrackbar(
            "White V Min",
            WINDOW_NAME,
            self.hsv_params["white_v_min"],
            255,
            self._on_trackbar,
        )
        cv2.createTrackbar(
            "White S Max",
            WINDOW_NAME,
            self.hsv_params["white_s_max"],
            255,
            self._on_trackbar,
        )
        cv2.createTrackbar(
            "Min Pixels",
            WINDOW_NAME,
            self.hsv_params["min_pixels"],
            1000,
            self._on_trackbar,
        )

    def _on_trackbar(self, value):
        """트랙바 콜백 (아무것도 하지 않음)"""
        pass

    def get_trackbar_values(self):
        """현재 트랙바 값 가져오기"""
        self.hsv_params["white_v_min"] = cv2.getTrackbarPos("White V Min", WINDOW_NAME)
        self.hsv_params["white_s_max"] = cv2.getTrackbarPos("White S Max", WINDOW_NAME)
        self.hsv_params["min_pixels"] = cv2.getTrackbarPos("Min Pixels", WINDOW_NAME)

    def capture_frame(self) -> Tuple[np.ndarray, float]:
        """
        단일 프레임 캡처

        Returns:
            (이미지, 캡처 시간)
        """
        start_time = time.time()

        try:
            response = self.session.get(CAPTURE_URL, timeout=2, stream=True)

            if response.status_code == 200:
                # 청크 단위로 읽기
                content = b""
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        content += chunk

                # 이미지 디코딩
                nparr = np.frombuffer(content, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                capture_time = (time.time() - start_time) * 1000  # ms
                return image, capture_time

        except Exception as e:
            print(f"⚠️ 캡처 실패: {e}")
            self.stats["errors"] += 1

        return None, 0

    def process_frame(self, image: np.ndarray) -> Dict[str, Any]:
        """
        프레임 분석

        Args:
            image: 입력 이미지 (BGR)

        Returns:
            분석 결과 딕셔너리
        """
        process_start = time.time()

        try:
            # 1. CLAHE 전처리
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            enhanced = self.clahe.apply(gray)
            enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

            # 2. 가우시안 블러
            blurred = cv2.GaussianBlur(enhanced_bgr, (5, 5), 0)

            # 3. ROI 추출 (하단 25%)
            height, width = blurred.shape[:2]
            roi_y_start = int(height * 0.75)
            roi = blurred[roi_y_start:height, 0:width]

            # 4. HSV 변환 및 차선 마스크 생성
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

            # 트랙바 값으로 흰색 차선 검출
            white_v_min = self.hsv_params["white_v_min"]
            white_s_max = self.hsv_params["white_s_max"]

            lower_white = np.array([0, 0, white_v_min])
            upper_white = np.array([180, white_s_max, 255])
            mask_white = cv2.inRange(hsv, lower_white, upper_white)

            # 빨간색 차선
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)

            lower_red2 = np.array([160, 100, 100])
            upper_red2 = np.array([180, 255, 255])
            mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)

            mask_red = cv2.bitwise_or(mask_red1, mask_red2)

            # 통합 마스크
            mask = cv2.bitwise_or(mask_white, mask_red)

            # 5. 노이즈 제거
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

            # 6. 히스토그램 계산 (3등분)
            third = width // 3
            left_sum = np.sum(mask[:, 0:third] == 255)
            center_sum = np.sum(mask[:, third : third * 2] == 255)
            right_sum = np.sum(mask[:, third * 2 : width] == 255)

            histogram = {
                "left": int(left_sum),
                "center": int(center_sum),
                "right": int(right_sum),
            }

            # 7. 조향 판단
            command, confidence = self._judge_steering(histogram)

            # 8. 분석 이미지 생성
            analysis_image = self._draw_analysis(
                image.copy(), mask, roi_y_start, histogram, command, confidence
            )

            process_time = (time.time() - process_start) * 1000  # ms

            return {
                "analysis_image": analysis_image,
                "mask": mask,
                "histogram": histogram,
                "command": command,
                "confidence": confidence,
                "process_time": process_time,
                "roi_y_start": roi_y_start,
            }

        except Exception as e:
            print(f"⚠️ 분석 실패: {e}")
            return {
                "analysis_image": image.copy(),
                "mask": None,
                "histogram": {"left": 0, "center": 0, "right": 0},
                "command": "stop",
                "confidence": 0.0,
                "process_time": 0,
                "roi_y_start": 0,
            }

    def _judge_steering(self, histogram: Dict[str, int]) -> Tuple[str, float]:
        """
        조향 판단

        Args:
            histogram: 히스토그램 데이터

        Returns:
            (명령, 신뢰도)
        """
        left = histogram["left"]
        center = histogram["center"]
        right = histogram["right"]
        total = left + center + right

        min_pixels = self.hsv_params["min_pixels"]

        # 차선이 거의 없으면 정지
        if total < min_pixels:
            return "stop", 0.0

        # 정규화
        left_ratio = left / total if total > 0 else 0
        center_ratio = center / total if total > 0 else 0
        right_ratio = right / total if total > 0 else 0

        # 데드존 (좌우 차이가 적으면 center)
        deadzone = 0.15
        if abs(left_ratio - right_ratio) < deadzone:
            return "center", center_ratio

        # 좌우 편향 판단
        bias_ratio = 1.3
        if left_ratio > right_ratio * bias_ratio:
            confidence = min(left_ratio / (left_ratio + right_ratio), 1.0)
            return "left", confidence
        elif right_ratio > left_ratio * bias_ratio:
            confidence = min(right_ratio / (left_ratio + right_ratio), 1.0)
            return "right", confidence
        else:
            return "center", center_ratio

    def _draw_analysis(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        roi_y_start: int,
        histogram: Dict[str, int],
        command: str,
        confidence: float,
    ) -> np.ndarray:
        """
        분석 이미지 생성

        Args:
            image: 원본 이미지
            mask: 차선 마스크
            roi_y_start: ROI 시작 Y 좌표
            histogram: 히스토그램
            command: 명령
            confidence: 신뢰도

        Returns:
            분석 이미지
        """
        height, width = image.shape[:2]

        # 마스크를 컬러로 변환
        mask_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

        # ROI 영역에 마스크 오버레이
        roi_h = height - roi_y_start
        overlay = image.copy()
        overlay[roi_y_start:height, 0:width] = cv2.addWeighted(
            overlay[roi_y_start:height, 0:width], 0.7, mask_colored, 0.3, 0
        )

        # ROI 경계선
        cv2.line(overlay, (0, roi_y_start), (width, roi_y_start), (255, 255, 0), 2)

        # 3등분 선
        third = width // 3
        cv2.line(overlay, (third, roi_y_start), (third, height), (100, 100, 100), 1)
        cv2.line(
            overlay, (third * 2, roi_y_start), (third * 2, height), (100, 100, 100), 1
        )

        # 명령 표시
        command_text = command.upper()
        color = {
            "left": (0, 165, 255),  # 주황색
            "right": (255, 0, 255),  # 자홍색
            "center": (0, 255, 0),  # 초록색
            "stop": (0, 0, 255),  # 빨간색
        }.get(command, (255, 255, 255))

        cv2.putText(
            overlay,
            f">>> {command_text} <<<",
            (10, 40),
            cv2.FONT_HERSHEY_DUPLEX,
            1.2,
            color,
            3,
        )

        # 히스토그램 표시
        left = histogram["left"]
        center = histogram["center"]
        right = histogram["right"]

        cv2.putText(
            overlay,
            f"L:{left:4d}  C:{center:4d}  R:{right:4d}",
            (10, height - 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        # 신뢰도 표시
        cv2.putText(
            overlay,
            f"신뢰도: {confidence*100:.1f}%",
            (10, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        return overlay

    def run(self):
        """메인 루프 실행"""
        print("=" * 60)
        print("🚗 실시간 자율주행 분석 도구")
        print("=" * 60)
        print(f"ESP32-CAM 주소: {ESP32_IP}")
        print(f"타겟 FPS: {TARGET_FPS}")
        print()
        print("💡 사용법:")
        print("  - 트랙바를 조정하여 파라미터 변경")
        print("  - 'q' 키를 누르면 종료")
        print("=" * 60)
        print()

        # 트랙바 생성
        self.create_trackbars()

        # FPS 제어
        frame_interval = 1.0 / TARGET_FPS
        last_frame_time = 0

        # FPS 계산
        fps_counter = 0
        fps_start = time.time()
        current_fps = 0

        try:
            while True:
                current_time = time.time()

                # FPS 제한
                if current_time - last_frame_time < frame_interval:
                    time.sleep(0.01)
                    continue

                last_frame_time = current_time

                # 트랙바 값 업데이트
                self.get_trackbar_values()

                # 프레임 캡처
                capture_start = time.time()
                image, capture_time = self.capture_frame()

                if image is None:
                    print("⚠️ 캡처 실패 - 재시도 중...")
                    time.sleep(0.1)
                    continue

                self.stats["frames"] += 1
                fps_counter += 1

                # FPS 계산 (1초마다)
                if current_time - fps_start >= 1.0:
                    current_fps = fps_counter
                    fps_counter = 0
                    fps_start = current_time

                # 프레임 분석
                result = self.process_frame(image)

                total_time = (time.time() - capture_start) * 1000

                # 원본 이미지에 정보 추가
                original = image.copy()
                cv2.putText(
                    original,
                    "원본 이미지",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 255),
                    2,
                )

                # 분석 이미지
                analysis = result["analysis_image"]

                # 시간 정보 표시
                cv2.putText(
                    analysis,
                    f"캡처: {capture_time:.1f}ms",
                    (10, height - 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (200, 200, 200),
                    1,
                )

                cv2.putText(
                    analysis,
                    f"분석: {result['process_time']:.1f}ms",
                    (10, height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (200, 200, 200),
                    1,
                )

                cv2.putText(
                    analysis,
                    f"전체: {total_time:.1f}ms",
                    (150, height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (200, 200, 200),
                    1,
                )

                # FPS 표시
                cv2.putText(
                    analysis,
                    f"FPS: {current_fps}",
                    (width - 120, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )

                # 좌우 결합
                height, width = original.shape[:2]
                combined = cv2.hconcat([original, analysis])

                # 화면 표시
                cv2.imshow(WINDOW_NAME, combined)

                # 키 입력 처리
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    print("\n사용자가 종료 요청")
                    break

        except KeyboardInterrupt:
            print("\n\n사용자가 중단 (Ctrl+C)")
        except Exception as e:
            print(f"\n⚠️ 오류 발생: {e}")
            import traceback

            traceback.print_exc()
        finally:
            # 통계 출력
            elapsed = time.time() - self.stats["start_time"]
            avg_fps = self.stats["frames"] / elapsed if elapsed > 0 else 0

            print("\n" + "=" * 60)
            print("📊 실행 통계")
            print("=" * 60)
            print(f"처리된 프레임: {self.stats['frames']}")
            print(f"오류 발생: {self.stats['errors']}")
            print(f"실행 시간: {elapsed:.1f}초")
            print(f"평균 FPS: {avg_fps:.1f}")
            print("=" * 60)

            cv2.destroyAllWindows()
            print("\n종료")


def main():
    """메인 함수"""
    analyzer = RealtimeAnalyzer()
    analyzer.run()


if __name__ == "__main__":
    main()
