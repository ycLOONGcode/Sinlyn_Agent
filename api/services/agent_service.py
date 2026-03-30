# -*- coding: utf-8 -*-
"""
Agent工具调用业务服务
封装Agent工具调用逻辑
"""

from agent.react_agent import ReactAgent
from agent.tools import agent_tools
from utils.logger_handler import logger


class AgentService:
    """
    Agent工具调用业务服务类
    """
    
    def __init__(self, agent: ReactAgent):
        """
        初始化Agent服务
        
        Args:
            agent: ReactAgent实例
        """
        self.agent = agent
    
    async def execute_tool(self, tool_name: str, params: dict) -> dict:
        """
        执行指定的Agent工具
        
        Args:
            tool_name: 工具名称
            params: 工具参数
        
        Returns:
            执行结果字典
        """
        logger.info(f"[Agent服务] 执行工具: {tool_name}, 参数: {params}")
        
        tool_map = {
            "rag_summarize": agent_tools.rag_summarize,
            "get_weather": agent_tools.get_weather,
            "get_user_location": agent_tools.get_user_location,
            "get_user_id": agent_tools.get_user_id,
            "get_current_month": agent_tools.get_current_month,
            "fetch_external_data": agent_tools.fetch_external_data,
            "fill_context_for_report": agent_tools.fill_context_for_report,
        }
        
        if tool_name not in tool_map:
            raise ValueError(f"工具 {tool_name} 不存在")
        
        try:
            tool_func = tool_map[tool_name]
            
            if params:
                result = tool_func(**params)
            else:
                result = tool_func()
            
            logger.info(f"[Agent服务] 工具 {tool_name} 执行成功")
            
            return {
                "result": str(result),
                "success": True,
                "tool_name": tool_name
            }
        except Exception as e:
            logger.error(f"[Agent服务] 工具 {tool_name} 执行失败: {str(e)}")
            raise e
