# 智扫通智能客服API使用指南

## 概述

智扫通智能客服API提供基于RAG与Agent的扫地机器人智能客服服务，支持对话、Agent工具调用、报告生成等功能。

## 服务信息

- **服务名称**: 智扫通智能客服API
- **版本**: 1.0.0
- **基础URL**: `http://localhost:8000`
- **API文档**: `http://localhost:8000/docs` (Swagger UI)
- **API文档**: `http://localhost:8000/redoc` (ReDoc)

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements_api.txt
```

### 2. 启动服务

```bash
# 方式一：使用启动脚本
python scripts/start_api_server.py

# 方式二：直接使用uvicorn
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# 方式三：开发模式（支持热重载）
python -m uvicorn api.main:app --reload
```

### 3. 访问API文档

启动服务后，访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API接口说明

### 对话接口

#### 单轮对话

**接口**: `POST /api/v1/chat/message`

**请求示例**:
```json
{
  "message": "小户型适合哪些扫地机器人",
  "session_id": "2026-03-30_10-30-00",
  "robot_nickname": "小智",
  "nature": "专业、简洁、亲切"
}
```

**响应示例**:
```json
{
  "response": "对于小户型，我推荐以下几款扫地机器人...",
  "session_id": "2026-03-30_10-30-00",
  "tools_called": ["rag_summarize"],
  "timestamp": "2026-03-30T10:30:15.123456"
}
```

#### 流式对话

**接口**: `POST /api/v1/chat/stream`

**请求示例**: 同单轮对话

**响应**: Server-Sent Events (SSE)流式响应

#### 获取会话列表

**接口**: `GET /api/v1/chat/sessions`

**响应示例**:
```json
{
  "sessions": [
    "2026-03-30_10-30-00",
    "2026-03-30_09-15-00"
  ]
}
```

#### 加载指定会话

**接口**: `GET /api/v1/chat/sessions/{session_id}`

**响应示例**:
```json
{
  "session_id": "2026-03-30_10-30-00",
  "robot_nickname": "小智",
  "nature": "专业、简洁、亲切",
  "messages": [
    {
      "role": "user",
      "content": "小户型适合哪些扫地机器人"
    },
    {
      "role": "assistant",
      "content": "对于小户型，我推荐以下几款扫地机器人..."
    }
  ]
}
```

#### 删除会话

**接口**: `DELETE /api/v1/chat/sessions/{session_id}`

**响应示例**:
```json
{
  "success": true,
  "message": "会话已删除"
}
```

### Agent工具接口

#### 获取工具列表

**接口**: `GET /api/v1/agent/tools`

**响应示例**:
```json
{
  "tools": [
    {
      "name": "rag_summarize",
      "description": "从向量存储中检索参考资料"
    },
    {
      "name": "get_weather",
      "description": "获取指定城市的天气"
    },
    {
      "name": "get_user_location",
      "description": "获取用户所在城市的名称"
    },
    {
      "name": "get_user_id",
      "description": "获取用户的ID"
    },
    {
      "name": "get_current_month",
      "description": "获取当前月份"
    },
    {
      "name": "fetch_external_data",
      "description": "从外部系统中获取指定用户在指定月份的使用记录"
    },
    {
      "name": "fill_context_for_report",
      "description": "调用后触发中间件自动为报告生成的场景动态注入上下文信息"
    }
  ]
}
```

#### 调用指定工具

**接口**: `POST /api/v1/agent/tools/{tool_name}`

**请求示例** (调用get_weather工具):
```json
{
  "params": {
    "city": "深圳"
  }
}
```

**响应示例**:
```json
{
  "result": "城市深圳天气为晴天，气温26摄氏度，空气湿度50%，南风1级，AQI21，最近6小时降雨概率极低",
  "success": true,
  "tool_name": "get_weather"
}
```

### 报告生成接口

#### 生成使用报告

**接口**: `POST /api/v1/report/generate`

**请求示例**:
```json
{
  "user_id": "1001",
  "month": "2025-06"
}
```

**响应示例**:
```json
{
  "report": "# 黑马程序员扫地机器人使用情况报告与保养建议\n\n## 一、使用概况\n...",
  "user_id": "1001",
  "month": "2025-06",
  "generated_at": "2026-03-30T10:30:15.123456"
}
```

### 系统接口

#### 健康检查

**接口**: `GET /api/v1/health`

**响应示例**:
```json
{
  "status": "healthy",
  "service": "智扫通智能客服API",
  "version": "1.0.0",
  "timestamp": "2026-03-30T10:30:15.123456"
}
```

#### 获取版本信息

**接口**: `GET /api/v1/version`

**响应示例**:
```json
{
  "service": "智扫通智能客服API",
  "version": "1.0.0",
  "description": "基于RAG与Agent的扫地机器人智能客服API服务"
}
```

## 使用示例

### Python示例

```python
import requests

# 单轮对话
response = requests.post(
    "http://localhost:8000/api/v1/chat/message",
    json={
        "message": "小户型适合哪些扫地机器人"
    }
)
print(response.json())

# 调用工具
response = requests.post(
    "http://localhost:8000/api/v1/agent/tools/get_weather",
    json={
        "params": {
            "city": "深圳"
        }
    }
)
print(response.json())

# 生成报告
response = requests.post(
    "http://localhost:8000/api/v1/report/generate",
    json={
        "user_id": "1001",
        "month": "2025-06"
    }
)
print(response.json())
```

### cURL示例

```bash
# 单轮对话
curl -X POST "http://localhost:8000/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "小户型适合哪些扫地机器人"}'

# 调用工具
curl -X POST "http://localhost:8000/api/v1/agent/tools/get_weather" \
  -H "Content-Type: application/json" \
  -d '{"params": {"city": "深圳"}}'

# 生成报告
curl -X POST "http://localhost:8000/api/v1/report/generate" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "1001", "month": "2025-06"}'
```

## 并行运行

FastAPI服务可以与原Streamlit应用并行运行：

```bash
# 终端1：启动FastAPI服务
python scripts/start_api_server.py

# 终端2：启动Streamlit应用
python scripts/start_streamlit_app.py
```

- FastAPI服务: http://localhost:8000
- Streamlit应用: http://localhost:8501

## 测试

运行API测试：

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_chat_api.py -v
pytest tests/test_agent_api.py -v
pytest tests/test_report_api.py -v
```

## 注意事项

1. **会话管理**: 会话数据存储在`sessions/`目录，FastAPI与Streamlit共用同一个会话存储
2. **并发安全**: 使用文件锁保证并发写入安全
3. **日志记录**: 所有API请求和响应都会记录到`logs/`目录
4. **CORS配置**: 默认允许所有源访问，生产环境建议限制允许的源

## 故障排查

### 服务无法启动

1. 检查端口8000是否被占用
2. 检查依赖是否正确安装
3. 查看日志文件`logs/agent_YYYYMMDD.log`

### API调用失败

1. 检查服务是否正常运行
2. 查看API文档确认请求格式
3. 查看日志文件获取详细错误信息

### Agent调用失败

1. 检查配置文件`config/rag.yml`和`config/chroma.yml`
2. 检查向量数据库`chroma_db/`是否正确初始化
3. 检查大模型API密钥是否正确配置

## 技术支持

如有问题，请查看：
- API文档: http://localhost:8000/docs
- 日志文件: logs/目录
- 测试用例: tests/目录
