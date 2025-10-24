#!/usr/bin/env python3
"""
실시간 자율주행 분석 도구 (모듈화 버전)

ESP32-CAM의 /capture를 사용하여 1초당 3 프레임을 분석하고
원본 이미지와 분석 결과를 동시에 표시합니다.

사용법:
    python realtime_analysis_v2.py
"""

from realtime_analysis import RealtimeAnalyzer


def main():
    """메인 함수"""
    # 분석기 생성
    analyzer = RealtimeAnalyzer()

    # 초기 설정
    analyzer.setup()

    # 실행
    analyzer.run()


if __name__ == "__main__":
    main()
