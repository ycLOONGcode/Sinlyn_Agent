# -*- coding: utf-8 -*-
"""
对话接口测试
测试FastAPI对话相关接口
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_check():
    """测试健康检查接口"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data
    print("✓ 健康检查接口测试通过")


def test_get_version():
    """测试获取版本信息接口"""
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data
    print("✓ 版本信息接口测试通过")


def test_chat_message():
    """测试单轮对话接口"""
    response = client.post(
        "/api/v1/chat/message",
        json={
            "message": "我最近有点焦虑"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "session_id" in data
    assert len(data["response"]) > 0
    print(f"✓ 单轮对话接口测试通过，会话ID: {data['session_id']}")


def test_chat_message_with_session():
    """测试带会话ID的对话接口"""
    response = client.post(
        "/api/v1/chat/message",
        json={
            "message": "我最近有点焦虑",
            "session_id": "test_session_001",
            "robot_nickname": "小心聆",
            "nature": "专业、耐心、亲切"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "test_session_001"
    print("✓ 带会话ID的对话接口测试通过")


def test_list_sessions():
    """测试获取会话列表接口"""
    response = client.get("/api/v1/chat/sessions")
    assert response.status_code == 200
    data = response.json()
    assert "sessions" in data
    assert isinstance(data["sessions"], list)
    print(f"✓ 获取会话列表接口测试通过，共{len(data['sessions'])}个会话")


def test_get_session():
    """测试加载指定会话接口"""
    response = client.post(
        "/api/v1/chat/message",
        json={
            "message": "测试消息"
        }
    )
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    
    response = client.get(f"/api/v1/chat/sessions/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert "messages" in data
    print("✓ 加载指定会话接口测试通过")


def test_delete_session():
    """测试删除会话接口"""
    response = client.post(
        "/api/v1/chat/message",
        json={
            "message": "测试删除会话"
        }
    )
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    
    response = client.delete(f"/api/v1/chat/sessions/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    print("✓ 删除会话接口测试通过")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
