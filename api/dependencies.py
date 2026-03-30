# -*- coding: utf-8 -*-
"""
依赖注入管理
管理Agent实例、会话历史等可复用依赖项
"""

from functools import lru_cache
from pathlib import Path

from agent.react_agent import ReactAgent
from utils.logger_handler import logger


@lru_cache()
def get_agent() -> ReactAgent:
    """
    获取Agent单例实例
    使用lru_cache确保整个应用生命周期内只有一个Agent实例
    """
    logger.debug("[依赖注入] 创建ReactAgent实例")
    return ReactAgent()


def get_sessions_dir() -> Path:
    """
    获取会话目录路径
    复用原项目的sessions目录
    """
    from utils.path_tool import get_abs_path
    return Path(get_abs_path("sessions"))


def get_session_file_path(session_id: str) -> Path:
    """
    获取指定会话文件的完整路径
    """
    sessions_dir = get_sessions_dir()
    return sessions_dir / f"{session_id}.json"
