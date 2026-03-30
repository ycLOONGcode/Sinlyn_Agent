# -*- coding: utf-8 -*-
"""
FastAPI服务启动脚本
独立启动FastAPI服务，可与Streamlit并行运行
"""

import uvicorn
from api.config.settings import settings

if __name__ == "__main__":
    print(f"正在启动 {settings.app_name} v{settings.app_version}...")
    print(f"服务地址: http://{settings.host}:{settings.port}")
    print(f"API文档: http://{settings.host}:{settings.port}/docs")
    print(f"调试模式: {settings.debug}")
    print("-" * 50)
    
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
