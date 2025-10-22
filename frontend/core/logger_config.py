"""
로거 설정 모듈
애플리케이션 전체의 로깅 설정을 관리
"""

import logging
import config


def setup_logger():
    """
    로깅 설정 초기화

    config.py의 설정값을 기반으로 로거를 구성합니다.
    """
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL), format=config.LOG_FORMAT
    )

    logger = logging.getLogger(__name__)
    logger.info("로거 설정 완료")

    return logger
