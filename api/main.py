# -*- coding: utf-8 -*-
"""
FastAPI应用主入口
与原项目app.py（Streamlit）并行运行，提供RESTful API服务
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config.settings import settings
from api.middleware.logging import LoggingMiddleware
from api.middleware.cors import cors_middleware_config
from api.routers import chat, agent, report, health

app = FastAPI(
    title=settings.app_name,
    description="基于RAG与Agent的心聆AgentAPI服务",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(CORSMiddleware, **cors_middleware_config)

app.add_middleware(LoggingMiddleware)

app.include_router(chat.router, prefix="/api/v1/chat", tags=["对话"])
app.include_router(agent.router, prefix="/api/v1/agent", tags=["Agent工具"])
app.include_router(report.router, prefix="/api/v1/report", tags=["报告生成"])
app.include_router(health.router, prefix="/api/v1", tags=["系统"])


@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化操作"""
    from utils.logger_handler import logger
    logger.info(f"[FastAPI] {settings.app_name} v{settings.app_version} 启动成功")
    logger.info(f"[FastAPI] 服务地址: http://{settings.host}:{settings.port}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理操作"""
    from utils.logger_handler import logger
    logger.info("[FastAPI] 服务已关闭")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
