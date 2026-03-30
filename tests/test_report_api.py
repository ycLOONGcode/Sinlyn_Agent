# -*- coding: utf-8 -*-
"""
报告接口测试
测试FastAPI报告生成接口
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_generate_report_auto_params():
    """测试自动获取参数生成报告"""
    response = client.post(
        "/api/v1/report/generate",
        json={}
    )
    assert response.status_code == 200
    data = response.json()
    assert "report" in data
    assert "user_id" in data
    assert "month" in data
    assert "generated_at" in data
    assert len(data["report"]) > 0
    print(f"✓ 自动获取参数生成报告测试通过，用户ID: {data['user_id']}, 月份: {data['month']}")


def test_generate_report_with_params():
    """测试指定参数生成报告"""
    response = client.post(
        "/api/v1/report/generate",
        json={
            "user_id": "1001",
            "month": "2025-06"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "1001"
    assert data["month"] == "2025-06"
    assert "report" in data
    assert len(data["report"]) > 0
    print("✓ 指定参数生成报告测试通过")


def test_generate_report_with_user_id_only():
    """测试仅指定用户ID生成报告"""
    response = client.post(
        "/api/v1/report/generate",
        json={
            "user_id": "1002"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "1002"
    assert "month" in data
    assert "report" in data
    print("✓ 仅指定用户ID生成报告测试通过")


def test_generate_report_with_month_only():
    """测试仅指定月份生成报告"""
    response = client.post(
        "/api/v1/report/generate",
        json={
            "month": "2025-03"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["month"] == "2025-03"
    assert "user_id" in data
    assert "report" in data
    print("✓ 仅指定月份生成报告测试通过")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
