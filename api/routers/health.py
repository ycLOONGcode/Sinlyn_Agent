# -*- coding: utf-8 -*-
"""
健康检查路由
提供服务健康状态检查接口
"""

from datetime import datetime
from fastapi import APIRouter

from api.config.settings import settings
from utils.logger_handler import logger

router = APIRouter()


@router.get("/health", summary="健康检查")
async def health_check():
    """
    健康检查接口
    
    返回服务状态、版本信息、时间戳
    """
    logger.debug("[健康检查] 执行健康检查")
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/version", summary="获取版本信息")
async def get_version():
    """
    获取服务版本信息
    """
    logger.debug("[版本信息] 获取版本信息")
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "description": "基于RAG与Agent的心聆AgentAPI服务"
    }
