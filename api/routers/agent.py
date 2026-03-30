# -*- coding: utf-8 -*-
"""
Agent工具调用路由
提供直接调用Agent工具的接口
"""

from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status

from agent.react_agent import ReactAgent
from agent.tools.agent_tools import (
    rag_summarize,
    get_weather,
    get_user_location,
    get_user_id,
    get_current_month,
    fetch_external_data,
    fill_context_for_report
)
from api.dependencies import get_agent
from api.schemas.agent import ToolCallRequest, ToolCallResponse, ToolListResponse
from utils.logger_handler import logger

router = APIRouter()

TOOL_FUNCTIONS = {
    "rag_summarize": rag_summarize,
    "get_weather": get_weather,
    "get_user_location": get_user_location,
    "get_user_id": get_user_id,
    "get_current_month": get_current_month,
    "fetch_external_data": fetch_external_data,
    "fill_context_for_report": fill_context_for_report,
}


@router.get("/tools", response_model=ToolListResponse, summary="获取工具列表")
async def list_tools():
    """
    获取所有可用的Agent工具列表
    """
    tools_info = []
    for tool_name, tool_func in TOOL_FUNCTIONS.items():
        tools_info.append({
            "name": tool_name,
            "description": tool_func.description if hasattr(tool_func, 'description') else ""
        })
    
    logger.info(f"[Agent工具] 获取工具列表, 共{len(tools_info)}个工具")
    return ToolListResponse(tools=tools_info)


@router.post("/tools/{tool_name}", response_model=ToolCallResponse, summary="调用指定工具")
async def call_tool(
    tool_name: str,
    request: ToolCallRequest,
    agent: ReactAgent = Depends(get_agent)
):
    """
    调用指定的Agent工具
    
    - **tool_name**: 工具名称（rag_summarize, get_weather, get_user_location, get_user_id, get_current_month, fetch_external_data, fill_context_for_report）
    - **params**: 工具参数（JSON对象）
    """
    if tool_name not in TOOL_FUNCTIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工具 {tool_name} 不存在"
        )
    
    logger.info(f"[Agent工具] 调用工具: {tool_name}, 参数: {request.params}")
    
    try:
        tool_func = TOOL_FUNCTIONS[tool_name]
        
        if request.params:
            result = tool_func(**request.params)
        else:
            result = tool_func()
        
        logger.info(f"[Agent工具] 工具 {tool_name} 调用成功")
        
        return ToolCallResponse(
            result=str(result),
            success=True,
            tool_name=tool_name
        )
    except Exception as e:
        logger.error(f"[Agent工具] 工具 {tool_name} 调用失败: {str(e)}")
        return ToolCallResponse(
            result=f"调用失败: {str(e)}",
            success=False,
            tool_name=tool_name
        )
