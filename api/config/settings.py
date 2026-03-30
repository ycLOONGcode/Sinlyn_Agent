# -*- coding: utf-8 -*-
"""
FastAPI配置管理
管理FastAPI相关配置，复用原项目的配置文件
"""

from pydantic_settings import BaseSettings

from utils.config_handler import rag_conf, chroma_conf


class APISettings(BaseSettings):
    """
    FastAPI配置类
    """
    app_name: str = "智扫通智能客服API"
    app_version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    chat_model: str = rag_conf.get("chat_model_name", "qwen3-max")
    embedding_model: str = rag_conf.get("embedding_model_name", "text-embedding-v4")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = APISettings()
