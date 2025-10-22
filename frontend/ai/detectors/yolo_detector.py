"""
YOLO 객체 감지 모듈
YOLOv8 모델을 사용하여 이미지에서 객체를 감지하고 Bounding Box 정보를 반환
"""

import cv2
import numpy as np
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class YOLODetector:
    """YOLO 기반 객체 감지 클래스"""

    def __init__(
        self, model_path: Optional[str] = None, confidence_threshold: float = 0.5
    ):
        """
        YOLO 감지기 초기화

        Args:
            model_path: YOLO 모델 경로 (None이면 기본 YOLOv8m 사용)
            confidence_threshold: 감지 신뢰도 임계값 (0.0 ~ 1.0)
        """
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.model_loaded = False

        try:
            # PyTorch 2.6+ weights_only 문제 해결
            # torch.load를 패치하여 YOLO 모델 로드 시 weights_only=False 사용
            import torch

            # 원본 torch.load 함수 저장
            if not hasattr(torch, "_original_load"):
                torch._original_load = torch.load

                # weights_only=False를 기본값으로 하는 패치 함수
                def patched_load(*args, **kwargs):
                    if "weights_only" not in kwargs:
                        kwargs["weights_only"] = False
                    return torch._original_load(*args, **kwargs)

                torch.load = patched_load
                logger.info("PyTorch 2.6+ 호환 모드 활성화 (weights_only=False)")

            # Ultralytics YOLOv8 사용
            from ultralytics import YOLO

            if model_path:
                self.model = YOLO(model_path)
            else:
                # 기본 모델 사용 (yolov8m.pt - 중형, 정확도 높음)
                # yolov8n: 6MB, 빠름, 정확도 낮음
                # yolov8s: 22MB, 중간 속도, 중간 정확도
                # yolov8m: 52MB, 균형잡힌 성능, 정확도 높음 ⭐
                # yolov8l: 87MB, 느림, 매우 높은 정확도
                # yolov8x: 136MB, 매우 느림, 최고 정확도
                self.model = YOLO("yolov8m.pt")

            self.model_loaded = True
            logger.info(f"YOLO 모델 로드 완료: {model_path or 'yolov8m.pt'}")

        except ImportError:
            logger.error(
                "Ultralytics 패키지가 설치되지 않았습니다. pip install ultralytics 실행 필요"
            )
            self.model_loaded = False
        except Exception as e:
            logger.error(f"YOLO 모델 로드 실패: {e}")
            self.model_loaded = False

    def is_ready(self) -> bool:
        """
        모델이 사용 가능한 상태인지 확인

        Returns:
            모델 사용 가능 여부
        """
        return self.model_loaded and self.model is not None

    def detect_objects(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        이미지에서 객체 감지

        Args:
            image: OpenCV 이미지 (numpy array)

        Returns:
            감지된 객체 리스트 (각 객체는 label, confidence, bbox 정보 포함)
            예: [
                {
                    "label": "person",
                    "confidence": 0.92,
                    "bbox": {"x": 100, "y": 150, "width": 200, "height": 300},
                    "rect": {"x1": 100, "y1": 150, "x2": 300, "y2": 450}
                }
            ]
        """
        if not self.is_ready():
            logger.error("YOLO 모델이 로드되지 않았습니다")
            return []

        try:
            # YOLO 모델로 예측 수행
            results = self.model(image, conf=self.confidence_threshold, verbose=False)

            detected_objects = []

            # 결과 파싱
            for result in results:
                boxes = result.boxes

                for box in boxes:
                    # Bounding Box 좌표 (x1, y1, x2, y2)
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                    # 신뢰도
                    confidence = float(box.conf[0].cpu().numpy())

                    # 클래스 ID 및 이름
                    class_id = int(box.cls[0].cpu().numpy())
                    label = result.names[class_id]

                    # Width, Height 계산
                    width = int(x2 - x1)
                    height = int(y2 - y1)

                    # 객체 정보 저장
                    detected_objects.append(
                        {
                            "label": label,
                            "confidence": round(confidence, 2),
                            "bbox": {
                                "x": int(x1),
                                "y": int(y1),
                                "width": width,
                                "height": height,
                            },
                            "rect": {
                                "x1": int(x1),
                                "y1": int(y1),
                                "x2": int(x2),
                                "y2": int(y2),
                            },
                        }
                    )

            logger.info(f"객체 {len(detected_objects)}개 감지됨")
            return detected_objects

        except Exception as e:
            logger.error(f"객체 감지 실패: {e}")
            return []

    def detect_from_bytes(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        바이트 데이터에서 객체 감지

        Args:
            image_bytes: 이미지 바이트 데이터 (JPEG, PNG 등)

        Returns:
            감지된 객체 리스트
        """
        try:
            # 바이트를 numpy array로 변환
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if image is None:
                logger.error("이미지 디코딩 실패")
                return []

            return self.detect_objects(image)

        except Exception as e:
            logger.error(f"바이트 이미지 처리 실패: {e}")
            return []

    def draw_detections(
        self, image: np.ndarray, detections: List[Dict[str, Any]]
    ) -> np.ndarray:
        """
        이미지에 감지 결과 그리기 (Bounding Box + Label)

        Args:
            image: 원본 이미지
            detections: detect_objects() 결과

        Returns:
            Bounding Box가 그려진 이미지
        """
        result_image = image.copy()

        for detection in detections:
            label = detection["label"]
            confidence = detection["confidence"]
            rect = detection["rect"]

            # Bounding Box 그리기 (녹색, 두껍게)
            cv2.rectangle(
                result_image,
                (rect["x1"], rect["y1"]),
                (rect["x2"], rect["y2"]),
                (0, 255, 0),  # 녹색
                3,  # 두께 증가 (2 -> 3)
            )

            # 레이블 텍스트 (더 크게)
            text = f"{label} {confidence:.2f}"
            font_scale = 0.5  # 폰트 크기 증가 (0.5 -> 0.8)
            font_thickness = 2
            text_size = cv2.getTextSize(
                text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness
            )[0]

            # 텍스트 위치: Bounding Box 안쪽 상단
            text_x = rect["x1"] + 5  # 왼쪽에서 5픽셀 안쪽
            text_y = rect["y1"] + text_size[1] + 10  # 위에서 아래로 10픽셀 안쪽

            # 텍스트 배경 (반투명 검은색)
            padding = 5
            cv2.rectangle(
                result_image,
                (text_x - padding, text_y - text_size[1] - padding),
                (text_x + text_size[0] + padding, text_y + padding),
                (0, 0, 0),  # 검은색
                -1,  # 채우기
            )

            # 텍스트 그리기 (흰색, 더 두껍게)
            cv2.putText(
                result_image,
                text,
                (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                (255, 255, 255),  # 흰색
                font_thickness,
            )

        return result_image

    def get_detection_summary(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        감지 결과 요약 정보 생성

        Args:
            detections: detect_objects() 결과

        Returns:
            요약 정보 (총 객체 수, 클래스별 개수 등)
        """
        summary = {"total_objects": len(detections), "classes": {}}

        for detection in detections:
            label = detection["label"]
            if label in summary["classes"]:
                summary["classes"][label] += 1
            else:
                summary["classes"][label] = 1

        return summary
