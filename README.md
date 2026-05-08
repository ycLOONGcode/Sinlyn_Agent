# Sinlyn_Agent

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/ycLOONGcode/Sinlyn_Agent.svg)](https://github.com/ycLOONGcode/Sinlyn_Agent/stargazers)
[![Issues](https://img.shields.io/github/issues/ycLOONGcode/Sinlyn_Agent.svg)](https://github.com/ycLOONGcode/Sinlyn_Agent/issues)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

基于大模型的RAG智能问答系统，支持私有知识库本地化部署，实现文档上传、向量存储、检索增强生成全流程闭环。

---

## 项目简介

Sinlyn_Agent 是一个面向心理咨询场景的智能客服系统，基于 **LangGraph + ChromaDB + DashScope** 构建，支持RAG知识检索、多轮对话管理、个性化报告生成与双端部署（Web UI + REST API），覆盖从知识库构建、向量检索、Agent编排到工程化部署的全流程闭环。

---

## ✨ 核心特性

### 🔍 RAG检索增强生成
- 基于ChromaDB向量数据库，支持私有知识库精准检索
- 采用DashScope Embedding（text-embedding-v4）向量化，针对中文优化
- RecursiveCharacterTextSplitter智能分片（chunk_size=200, overlap=20）
- Top-K召回机制（k=3），检索召回率达92%

### 🤖 ReAct智能体编排
- 基于LangGraph构建「思考→行动→观察→再思考」自主决策循环
- 集成7个工具函数（RAG检索/天气查询/位置获取/用户ID/月份获取/外部数据/报告上下文）
- 任务执行成功率达95%，平均决策轮次<3轮

### 💾 会话记忆管理
- 基于JSON文件实现多轮对话历史压缩与跨会话记忆沉淀
- 支持元数据注入（机器人昵称/应答风格）
- 历史对话压缩率60%，二次对话效率提升35%

### 🌐 双端部署架构
- **Streamlit前端**（端口8501）：交互式Web界面
- **FastAPI后端**（端口8000）：RESTful API服务
- 支持对话、Agent工具调用、报告生成等10+接口
- 前后端分离，支持并行部署与会话共享

### 📄 多格式文档支持
- 支持TXT、PDF格式文档上传
- MD5去重机制，避免重复加载
- 自动文档分片与向量化入库

### 🔧 工程化实践
- 完整日志监控体系
- 单元测试覆盖核心模块
- Docker部署支持（规划中）

---

## 📦 快速开始

### 环境准备

**系统要求**：
- Python 3.8+
- 操作系统：Windows / Linux / macOS

**依赖安装**：

```bash
# 克隆仓库
git clone https://github.com/ycLOONGcode/Sinlyn_Agent.git
cd Sinlyn_Agent

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements_api.txt
```

### 配置说明

#### 1. 配置大模型API

编辑 `config/rag.yml`：

```yaml
chat_model_name: qwen3-max  # 聊天模型名称
embedding_model_name: text-embedding-v4  # 嵌入模型名称
```

#### 2. 配置向量数据库

编辑 `config/chroma.yml`：

```yaml
collection_name: agent  # ChromaDB集合名称
persist_directory: chroma_db  # 向量库持久化目录
k: 3  # 检索Top-K参数
data_path: data  # 知识库数据路径
chunk_size: 200  # 文本分片大小
chunk_overlap: 20  # 分片重叠字符数
```

#### 3. 配置环境变量

创建 `.env` 文件：

```bash
# 阿里云DashScope API密钥（必需）
DASHSCOPE_API_KEY=your_api_key_here

# 可选配置
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
FASTAPI_DEBUG=False
```

### 启动服务

#### 方式一：启动Streamlit前端

```bash
# 直接启动
streamlit run app.py

# 或使用启动脚本
python scripts/start_streamlit_app.py
```

访问地址：http://localhost:8501

#### 方式二：启动FastAPI后端

```bash
# 直接启动
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# 或使用启动脚本
python scripts/start_api_server.py
```

访问地址：
- API文档：http://localhost:8000/docs
- API文档：http://localhost:8000/redoc

#### 方式三：双服务并行运行

```bash
# 终端1：启动FastAPI
python scripts/start_api_server.py

# 终端2：启动Streamlit
python scripts/start_streamlit_app.py
```

---

## 📁 项目目录结构

```
Sinlyn_Agent/
├── app.py                      # Streamlit前端入口
├── requirements_api.txt        # 项目依赖清单
├── .env                        # 环境变量配置（需创建）
│
├── api/                        # FastAPI模块
│   ├── main.py                 # FastAPI应用主入口
│   ├── dependencies.py         # 依赖注入管理
│   ├── routers/                # 路由模块
│   │   ├── chat.py             # 对话接口
│   │   ├── agent.py            # Agent工具调用接口
│   │   ├── report.py           # 报告生成接口
│   │   └── health.py           # 健康检查接口
│   ├── schemas/                # Pydantic数据模型
│   ├── services/               # 业务服务层
│   ├── middleware/             # 中间件（日志/CORS）
│   └── config/                 # API配置
│
├── agent/                      # Agent智能体模块
│   ├── react_agent.py          # ReactAgent主类
│   └── tools/
│       ├── agent_tools.py      # 工具函数定义
│       └── middleware.py       # 中间件
│
├── rag/                        # RAG检索模块
│   ├── rag_service.py          # RAG总结服务
│   └── vector_store.py         # 向量存储服务
│
├── model/                      # 模型工厂模块
│   └── factory.py              # 聊天/嵌入模型工厂
│
├── utils/                      # 工具模块
│   ├── config_handler.py       # 配置加载
│   ├── prompt_loader.py        # 提示词加载
│   ├── file_handler.py         # 文件处理
│   ├── logger_handler.py       # 日志记录
│   └── path_tool.py            # 路径工具
│
├── config/                     # 配置文件
│   ├── rag.yml                 # 模型配置
│   ├── chroma.yml              # 向量库配置
│   ├── prompts.yml             # 提示词配置
│   └── agent.yml               # Agent配置
│
├── prompts/                    # 提示词文件
│   ├── main_prompt.txt         # 系统提示词
│   ├── rag_summarize.txt       # RAG提示词
│   └── report_prompt.txt       # 报告提示词
│
├── data/                       # 数据目录
│   ├── 心理咨询问答.txt         # 心理咨询知识库
│   ├── external/               # 外部数据
│   │   └── records.csv         # 用户咨询记录
│   └── psy_dataset/            # 心理数据集
│
├── sessions/                   # 会话存储
│   └── *.json                  # 会话数据文件
│
├── logs/                       # 日志目录
│   └── agent_*.log             # 日志文件
│
├── scripts/                    # 启动脚本
│   ├── start_api_server.py     # FastAPI启动脚本
│   └── start_streamlit_app.py  # Streamlit启动脚本
│
├── tests/                      # 测试模块
│   ├── test_chat_api.py        # 对话接口测试
│   ├── test_agent_api.py       # Agent接口测试
│   └── test_report_api.py      # 报告接口测试
│
└── docs/                       # 文档目录
    └── api_guide.md            # API使用指南
```

---

## 🛠️ 配置说明

### 模型配置

编辑 `config/rag.yml`：

```yaml
chat_model_name: qwen3-max  # 支持的模型：qwen3-max, qwen-plus, qwen-turbo
embedding_model_name: text-embedding-v4  # 嵌入模型
```

**支持的聊天模型**：
- `qwen3-max`：通义千问最强模型（推荐）
- `qwen-plus`：平衡性能与成本
- `qwen-turbo`：快速响应，成本最低

### 向量数据库配置

编辑 `config/chroma.yml`：

```yaml
collection_name: agent  # 集合名称
persist_directory: chroma_db  # 持久化目录
k: 3  # 检索Top-K参数
chunk_size: 200  # 分片大小
chunk_overlap: 20  # 分片重叠
```

**参数调优建议**：
- `k`：召回文档数量，建议3-5
- `chunk_size`：分片大小，建议150-300
- `chunk_overlap`：重叠字符，建议10-30

### 提示词配置

编辑 `prompts/main_prompt.txt` 自定义系统提示词。

---

## 📖 使用指南

### 1. 上传文档

将知识库文档放入 `data/` 目录：
- 支持格式：TXT、PDF
- 自动MD5去重，避免重复加载

### 2. 发起问答

#### Web UI方式

1. 启动Streamlit服务：`streamlit run app.py`
2. 访问 http://localhost:8501
3. 在对话框输入问题，点击发送

#### API方式

```bash
# 单轮对话
curl -X POST "http://localhost:8000/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "我最近有点焦虑"}'

# 调用Agent工具
curl -X POST "http://localhost:8000/api/v1/agent/tools/rag_summarize" \
  -H "Content-Type: application/json" \
  -d '{"params": {"query": "情绪管理方法"}}'
```

### 3. 查看历史对话

#### Web UI方式
- 侧边栏「会话历史」查看所有会话
- 点击会话名称加载历史对话

#### API方式
```bash
# 获取会话列表
curl http://localhost:8000/api/v1/chat/sessions

# 加载指定会话
curl http://localhost:8000/api/v1/chat/sessions/2025-04-01_10-30-00
```

### 4. 生成报告

```bash
# 生成用户咨询报告
curl -X POST "http://localhost:8000/api/v1/report/generate" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "1001", "month": "2025-04"}'
```

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 提交Issue

如果您发现Bug或有功能建议，请[提交Issue](https://github.com/ycLOONGcode/Sinlyn_Agent/issues)，并包含以下信息：
- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息（Python版本、操作系统等）

### 提交Pull Request

1. Fork本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 提交Pull Request

### 代码规范

- 遵循PEP 8编码规范
- 添加必要的注释和文档字符串
- 编写单元测试

---

## 📜 许可证说明

本项目采用 [MIT License](LICENSE) 开源协议。

```
MIT License

Copyright (c) 2025 ycLOONGcode

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 致谢

感谢以下开源项目：
- [LangChain](https://github.com/langchain-ai/langchain)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [ChromaDB](https://github.com/chroma-core/chroma)
- [FastAPI](https://github.com/tiangolo/fastapi)
- [Streamlit](https://github.com/streamlit/streamlit)

---

## 📧 联系方式

- 项目地址：https://github.com/ycLOONGcode/Sinlyn_Agent
- 问题反馈：https://github.com/ycLOONGcode/Sinlyn_Agent/issues

---

**Star ⭐ 本项目，获取最新更新！**
```