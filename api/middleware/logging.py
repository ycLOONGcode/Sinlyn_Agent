# -*- coding: utf-8 -*-
"""
日志中间件
记录API请求日志，复用原项目的日志系统
"""

from datetime import datetime
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from utils.logger_handler import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    日志中间件
    记录所有API请求和响应
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        处理请求
        
        Args:
            request: HTTP请求对象
            call_next: 下一个中间件或路由处理器
        
        Returns:
            HTTP响应对象
        """
        start_time = None
        
        try:
            logger.info(f"[API] {request.method} {request.url.path}")
            
            start_time = datetime.now()
            
            response = await call_next(request)
            
            process_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(
                f"[API] 响应: {request.method} {request.url.path} "
                f"状态码: {response.status_code} "
                f"耗时: {process_time:.3f}秒"
            )
            
            return response
        except Exception as e:
            logger.error(f"[API] 请求处理异常: {request.method} {request.url.path}, 错误: {str(e)}")
            raise e


from datetime import datetime
