"""
서버 포트 선택 유틸리티 모듈
- 환경변수의 선호 포트를 읽고, 사용 중이면 사용 가능한 포트를 탐색
"""

import os
import socket
from typing import Optional


def _is_port_free(port: int) -> bool:
    """지정한 포트가 사용 가능하면 True를 반환합니다."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("0.0.0.0", port))
            return True
        except OSError:
            return False


def get_port_from_env(default_port: int) -> int:
    """환경변수 PORT에서 포트를 읽고 정수로 변환합니다. 실패 시 기본값을 반환합니다."""
    port_str: Optional[str] = os.environ.get("PORT")
    if not port_str:
        return default_port

    try:
        port_value = int(port_str)
    except ValueError:
        return default_port

    if port_value < 1 or port_value > 65535:
        return default_port

    return port_value


def select_server_port(preferred_port: int, max_tries: int = 20) -> int:
    """선호 포트에서 시작하여 사용 가능한 포트를 선택합니다.

    - preferred_port가 사용 중이면 +1씩 증가하며 최대 max_tries번 시도합니다.
    - 모든 시도가 실패하면 커널이 할당한 임시 포트를 사용합니다.
    """
    if preferred_port < 1:
        return _get_ephemeral_port()

    for offset in range(0, max_tries):
        candidate = preferred_port + offset
        if candidate > 65535:
            break
        if _is_port_free(candidate):
            return candidate

    return _get_ephemeral_port()


def _get_ephemeral_port() -> int:
    """커널이 할당하는 사용 가능 임시 포트를 반환합니다."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("0.0.0.0", 0))
        address, port = sock.getsockname()
        return port
