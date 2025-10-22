"""
로깅 설정 유틸리티
"""

import logging
import sys


def setup_logger(debug_mode: bool = False):
    """
    로거 설정

    Args:
        debug_mode: 디버그 모드 활성화 여부
    """
    level = logging.DEBUG if debug_mode else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("autonomous_driver.log", encoding="utf-8"),
        ],
    )

    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
