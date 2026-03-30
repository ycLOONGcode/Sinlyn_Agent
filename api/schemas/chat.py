# -*- coding: utf-8 -*-
"""
对话相关数据模型
定义对话接口的请求和响应数据结构
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    对话请求模型
    """
    message: str = Field(..., description="用户消息内容", min_length=1)
    session_id: Optional[str] = Field(None, description="会话ID，不传则创建新会话")
    robot_nickname: Optional[str] = Field("小智", description="机器人昵称")
    nature: Optional[str] = Field("专业、简洁、亲切", description="应答风格")


class ChatResponse(BaseModel):
    """
    对话响应模型
    """
    response: str = Field(..., description="AI回复内容")
    session_id: str = Field(..., description="会话ID")
    tools_called: List[str] = Field(default_factory=list, description="调用的工具列表")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")


class SessionInfo(BaseModel):
    """
    会话信息模型
    """
    session_id: str = Field(..., description="会话ID")
    created_at: Optional[str] = Field(None, description="创建时间")


class SessionListResponse(BaseModel):
    """
    会话列表响应模型
    """
    sessions: List[str] = Field(..., description="会话ID列表")


class SessionDetailResponse(BaseModel):
    """
    会话详情响应模型
    """
    session_id: str = Field(..., description="会话ID")
    robot_nickname: str = Field(..., description="机器人昵称")
    nature: str = Field(..., description="应答风格")
    messages: List[dict] = Field(..., description="消息历史")
