# -*- coding: utf-8 -*-
"""
Agent工具接口测试
测试FastAPI Agent工具调用接口
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_list_tools():
    """测试获取工具列表接口"""
    response = client.get("/api/v1/agent/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert isinstance(data["tools"], list)
    assert len(data["tools"]) > 0
    
    tool_names = [tool["name"] for tool in data["tools"]]
    expected_tools = [
        "rag_summarize",
        "get_weather",
        "get_user_location",
        "get_user_id",
        "get_current_month",
        "fetch_external_data",
        "fill_context_for_report"
    ]
    
    for expected_tool in expected_tools:
        assert expected_tool in tool_names, f"缺少工具: {expected_tool}"
    
    print(f"✓ 获取工具列表接口测试通过，共{len(data['tools'])}个工具")


def test_call_tool_rag_summarize():
    """测试调用rag_summarize工具"""
    response = client.post(
        "/api/v1/agent/tools/rag_summarize",
        json={
            "params": {
                "query": "我最近有点焦虑"
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["tool_name"] == "rag_summarize"
    assert "result" in data
    assert len(data["result"]) > 0
    print("✓ 调用rag_summarize工具测试通过")


def test_call_tool_get_weather():
    """测试调用get_weather工具"""
    response = client.post(
        "/api/v1/agent/tools/get_weather",
        json={
            "params": {
                "city": "深圳"
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["tool_name"] == "get_weather"
    assert "result" in data
    assert "深圳" in data["result"]
    print("✓ 调用get_weather工具测试通过")


def test_call_tool_get_user_location():
    """测试调用get_user_location工具"""
    response = client.post(
        "/api/v1/agent/tools/get_user_location",
        json={
            "params": {}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["tool_name"] == "get_user_location"
    assert "result" in data
    print("✓ 调用get_user_location工具测试通过")


def test_call_tool_get_user_id():
    """测试调用get_user_id工具"""
    response = client.post(
        "/api/v1/agent/tools/get_user_id",
        json={
            "params": {}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["tool_name"] == "get_user_id"
    assert "result" in data
    print("✓ 调用get_user_id工具测试通过")


def test_call_tool_get_current_month():
    """测试调用get_current_month工具"""
    response = client.post(
        "/api/v1/agent/tools/get_current_month",
        json={
            "params": {}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["tool_name"] == "get_current_month"
    assert "result" in data
    print("✓ 调用get_current_month工具测试通过")


def test_call_tool_fill_context_for_report():
    """测试调用fill_context_for_report工具"""
    response = client.post(
        "/api/v1/agent/tools/fill_context_for_report",
        json={
            "params": {}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["tool_name"] == "fill_context_for_report"
    print("✓ 调用fill_context_for_report工具测试通过")


def test_call_tool_fetch_external_data():
    """测试调用fetch_external_data工具"""
    response = client.post(
        "/api/v1/agent/tools/fetch_external_data",
        json={
            "params": {
                "user_id": "1001",
                "month": "2025-01"
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tool_name"] == "fetch_external_data"
    assert "result" in data
    print("✓ 调用fetch_external_data工具测试通过")


def test_call_tool_not_found():
    """测试调用不存在的工具"""
    response = client.post(
        "/api/v1/agent/tools/invalid_tool",
        json={
            "params": {}
        }
    )
    assert response.status_code == 404
    print("✓ 调用不存在工具的测试通过")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
