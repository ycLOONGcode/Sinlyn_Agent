# -*- coding: utf-8 -*-
"""
报告生成路由
提供用户使用报告生成接口
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from agent.react_agent import ReactAgent
from agent.tools.agent_tools import get_user_id, get_current_month, fetch_external_data, fill_context_for_report
from api.dependencies import get_agent
from api.schemas.report import ReportRequest, ReportResponse
from api.services.report_service import ReportService
from utils.logger_handler import logger

router = APIRouter()


@router.post("/generate", response_model=ReportResponse, summary="生成使用报告")
async def generate_report(
    request: ReportRequest,
    agent: ReactAgent = Depends(get_agent)
):
    """
    生成用户使用报告
    
    - **user_id**: 用户ID（可选，不传则自动获取）
    - **month**: 月份（可选，格式YYYY-MM，不传则使用当前月）
    """
    logger.info(f"[报告生成] 收到报告生成请求, user_id: {request.user_id}, month: {request.month}")
    
    service = ReportService(agent)
    
    try:
        report_data = await service.generate(request)
        
        logger.info(f"[报告生成] 报告生成成功, user_id: {report_data['user_id']}, month: {report_data['month']}")
        
        return ReportResponse(
            report=report_data["report"],
            user_id=report_data["user_id"],
            month=report_data["month"],
            generated_at=report_data["generated_at"]
        )
    except Exception as e:
        logger.error(f"[报告生成] 报告生成失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"报告生成失败: {str(e)}"
        )
