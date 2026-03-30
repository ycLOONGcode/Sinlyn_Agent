# -*- coding: utf-8 -*-
"""
对话业务服务
封装对话处理逻辑，复用原项目的Agent调用逻辑
"""

from typing import Tuple, List

from agent.react_agent import ReactAgent
from utils.logger_handler import logger


class ChatService:
    """
    对话业务服务类
    """
    
    def __init__(self, agent: ReactAgent):
        """
        初始化对话服务
        
        Args:
            agent: ReactAgent实例
        """
        self.agent = agent
    
    async def process_message(self, query: str) -> Tuple[str, List[str]]:
        """
        处理单轮对话
        
        Args:
            query: 构建好的查询（含历史对话和元数据）
        
        Returns:
            (response_text, tools_called): 响应文本和调用的工具列表
        """
        logger.info(f"[对话服务] 开始处理查询")
        
        response_chunks: List[str] = []
        tools_called: List[str] = []
        
        try:
            for chunk in self.agent.execute_stream(query):
                response_chunks.append(chunk)
            
            full_text = response_chunks[-1] if response_chunks else ""
            full_text = full_text.rstrip("\n") if isinstance(full_text, str) else str(full_text)
            
            logger.info(f"[对话服务] 查询处理完成")
            
            return full_text, tools_called
        except Exception as e:
            logger.error(f"[对话服务] 查询处理失败: {str(e)}")
            raise e
    
    async def process_stream(self, query: str):
        """
        处理流式对话
        
        Args:
            query: 构建好的查询（含历史对话和元数据）
        
        Yields:
            响应片段
        """
        logger.info(f"[对话服务] 开始流式处理")
        
        try:
            for chunk in self.agent.execute_stream(query):
                yield chunk
            
            logger.info(f"[对话服务] 流式处理完成")
        except Exception as e:
            logger.error(f"[对话服务] 流式处理失败: {str(e)}")
            raise e
