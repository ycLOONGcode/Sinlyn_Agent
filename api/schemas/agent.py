# -*- coding: utf-8 -*-
"""
Agent工具相关数据模型
定义Agent工具调用的请求和响应数据结构
"""

from typing import Dict, Any, List

from pydantic import BaseModel, Field


class ToolCallRequest(BaseModel):
    """
    工具调用请求模型
    """
    params: Dict[str, Any] = Field(default_factory=dict, description="工具参数")


class ToolCallResponse(BaseModel):
    """
    工具调用响应模型
    """
    result: str = Field(..., description="工具执行结果")
    success: bool = Field(..., description="是否成功")
    tool_name: str = Field(..., description="工具名称")


class ToolInfo(BaseModel):
    """
    工具信息模型
    """
    name: str = Field(..., description="工具名称")
    description: str = Field("", description="工具描述")


class ToolListResponse(BaseModel):
    """
    工具列表响应模型
    """
    tools: List[ToolInfo] = Field(..., description="工具列表")
