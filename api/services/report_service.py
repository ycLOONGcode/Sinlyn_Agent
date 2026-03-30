# -*- coding: utf-8 -*-
"""
报告生成业务服务
封装报告生成逻辑，复用原项目的Agent报告生成功能
"""

from datetime import datetime
from typing import Dict

from agent.react_agent import ReactAgent
from agent.tools import agent_tools
from utils.logger_handler import logger


class ReportService:
    """
    报告生成业务服务类
    """
    
    def __init__(self, agent: ReactAgent):
        """
        初始化报告服务
        
        Args:
            agent: ReactAgent实例
        """
        self.agent = agent
    
    async def generate(self, request: dict) -> Dict[str, str]:
        """
        生成用户使用报告
        
        Args:
            request: 报告请求字典，包含user_id和month
        
        Returns:
            报告数据字典，包含report、user_id、month、generated_at
        """
        logger.info(f"[报告服务] 开始生成报告")
        
        try:
            user_id = request.get("user_id")
            month = request.get("month")
            
            if not user_id:
                user_id = agent_tools.get_user_id()
                logger.info(f"[报告服务] 自动获取用户ID: {user_id}")
            
            if not month:
                month = agent_tools.get_current_month()
                logger.info(f"[报告服务] 自动获取月份: {month}")
            
            agent_tools.fill_context_for_report()
            logger.info(f"[报告服务] 已调用fill_context_for_report，触发报告生成模式")
            
            external_data = agent_tools.fetch_external_data(user_id, month)
            logger.info(f"[报告服务] 已获取用户 {user_id} 在 {month} 的使用记录")
            
            query = f"请为我生成{month}月份的使用报告，用户ID为{user_id}"
            
            response_chunks = []
            for chunk in self.agent.execute_stream(query):
                response_chunks.append(chunk)
            
            report = response_chunks[-1] if response_chunks else ""
            report = report.rstrip("\n") if isinstance(report, str) else str(report)
            
            logger.info(f"[报告服务] 报告生成完成")
            
            return {
                "report": report,
                "user_id": user_id,
                "month": month,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"[报告服务] 报告生成失败: {str(e)}")
            raise e
