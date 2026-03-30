# -*- coding: utf-8 -*-
"""
报告相关数据模型
定义报告生成接口的请求和响应数据结构
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    """
    报告生成请求模型
    """
    user_id: Optional[str] = Field(None, description="用户ID，不传则自动获取")
    month: Optional[str] = Field(None, description="月份，格式YYYY-MM，不传则使用当前月")


class ReportResponse(BaseModel):
    """
    报告生成响应模型
    """
    report: str = Field(..., description="Markdown格式报告")
    user_id: str = Field(..., description="用户ID")
    month: str = Field(..., description="报告月份")
    generated_at: datetime = Field(default_factory=datetime.now, description="生成时间戳")
