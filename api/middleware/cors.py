# -*- coding: utf-8 -*-
"""
CORS中间件
配置跨域资源共享策略
"""

from fastapi.middleware.cors import CORSMiddleware

# 允许的源列表
origins = [
    "http://localhost:8501",
    "http://localhost:3000",
    "http://127.0.0.1:8501",
    "http://127.0.0.1:3000",
]

# CORS中间件配置
cors_middleware_config = {
    "allow_origins": origins,
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
