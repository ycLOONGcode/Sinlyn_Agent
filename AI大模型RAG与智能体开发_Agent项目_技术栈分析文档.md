# AI大模型RAG与智能体开发项目 - 技术栈分析文档

## 项目概述

这是一个**基于RAG（检索增强生成）和Agent（智能体）技术的智能客服系统**，专门用于扫地机器人相关的问答服务。

## 核心技术栈

### 1. 编程语言
- **Python 3.10+** - 主要开发语言

### 2. Web框架与UI
- **Streamlit** - Web应用框架，用于构建交互式聊天界面
  - 聊天消息展示
  - 流式输出支持
  - 会话状态管理

**应用入口代码示例：**
```python
import time
import streamlit as st
from agent.react_agent import ReactAgent

st.title("智扫通机器人智能客服")
st.divider()

if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

if "message" not in st.session_state:
    st.session_state["message"] = []

for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input()

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    response_messages = []
    with st.spinner("智能客服思考中..."):
        res_stream = st.session_state["agent"].execute_stream(prompt)

        def capture(generator, cache_list):
            for chunk in generator:
                cache_list.append(chunk)
                for char in chunk:
                    time.sleep(0.01)
                    yield char

        st.chat_message("assistant").write_stream(capture(res_stream, response_messages))
        st.session_state["message"].append({"role": "assistant", "content": response_messages[-1]})
        st.rerun()
```

### 3. AI/LLM框架
- **LangChain** - 核心AI框架，包含多个子模块：
  - `langchain.agents` - Agent智能体框架
  - `langchain_core` - 核心组件
    - `documents` - 文档处理
    - `output_parsers` - 输出解析器（StrOutputParser）
    - `prompts` - 提示词模板（PromptTemplate）
    - `tools` - 工具定义
  - `langchain_community` - 社区扩展组件
    - `chat_models.tongyi` - 通义千问集成
    - `embeddings` - 嵌入模型
    - `document_loaders` - 文档加载器
  - `langchain_chroma` - Chroma向量数据库集成
  - `langchain_text_splitters` - 文本分割器
  - `langgraph` - LangGraph运行时框架
    - `runtime` - 运行时管理
    - `types` - 类型定义

**Agent核心代码示例：**
```python
from langchain.agents import create_agent
from model.factory import chat_model
from utils.prompt_loader import load_system_prompts
from agent.tools.agent_tools import (rag_summarize, get_weather, get_user_location, get_user_id,
                                     get_current_month, fetch_external_data, fill_context_for_report)
from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch


class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompts(),
            tools=[rag_summarize, get_weather, get_user_location, get_user_id,
                   get_current_month, fetch_external_data, fill_context_for_report],
            middleware=[monitor_tool, log_before_model, report_prompt_switch],
        )

    def execute_stream(self, query: str):
        input_dict = {
            "messages": [
                {"role": "user", "content": query},
            ]
        }

        for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
            latest_message = chunk["messages"][-1]
            if latest_message.content:
                yield latest_message.content.strip() + "\n"
```

### 4. 大语言模型
- **通义千问（Qwen）** - 阿里云大模型服务
  - **ChatTongyi** - 聊天模型（qwen3-max）
  - **DashScopeEmbeddings** - 嵌入模型（text-embedding-v4）

**模型工厂代码示例：**
```python
from abc import ABC, abstractmethod
from typing import Optional
from langchain_core.embeddings import Embeddings
from langchain_community.chat_models.tongyi import BaseChatModel
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.chat_models.tongyi import ChatTongyi
from utils.config_handler import rag_conf


class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass


class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return ChatTongyi(model=rag_conf["chat_model_name"])


class EmbeddingsFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return DashScopeEmbeddings(model=rag_conf["embedding_model_name"])


chat_model = ChatModelFactory().generator()
embed_model = EmbeddingsFactory().generator()
```

### 5. 向量数据库
- **Chroma** - 开源向量数据库
  - 向量存储和检索
  - 基于SQLite持久化存储
  - 支持相似度搜索（k=3）

**向量存储服务代码示例：**
```python
from langchain_chroma import Chroma
from langchain_core.documents import Document
from utils.config_handler import chroma_conf
from model.factory import embed_model
from langchain_text_splitters import RecursiveCharacterTextSplitter


class VectorStoreService:
    def __init__(self):
        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=embed_model,
            persist_directory=chroma_conf["persist_directory"],
        )

        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf["chunk_size"],
            chunk_overlap=chroma_conf["chunk_overlap"],
            separators=chroma_conf["separators"],
            length_function=len,
        )

    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_conf["k"]})
```

### 6. 文档处理
- **PyPDFLoader** - PDF文档加载器
- **TextLoader** - 文本文档加载器
- **RecursiveCharacterTextSplitter** - 递归文本分割器
  - chunk_size: 200
  - chunk_overlap: 20
  - 支持中英文分隔符

**文件处理代码示例：**
```python
import os
import hashlib
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader


def get_file_md5_hex(filepath: str):
    if not os.path.exists(filepath):
        logger.error(f"[md5计算]文件{filepath}不存在")
        return

    if not os.path.isfile(filepath):
        logger.error(f"[md5计算]路径{filepath}不是文件")
        return

    md5_obj = hashlib.md5()
    chunk_size = 4096

    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)
            md5_hex = md5_obj.hexdigest()
            return md5_hex
    except Exception as e:
        logger.error(f"计算文件{filepath}md5失败，{str(e)}")
        return None


def pdf_loader(filepath: str, passwd=None) -> list[Document]:
    return PyPDFLoader(filepath, passwd).load()


def txt_loader(filepath: str) -> list[Document]:
    return TextLoader(filepath, encoding="utf-8").load()
```

### 7. RAG服务
- **RagSummarizeService** - RAG总结服务类
  - 用户提问
  - 搜索参考资料
  - 将提问和参考资料提交给模型
  - 让模型总结回复

**RAG服务代码示例：**
```python
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts
from langchain_core.prompts import PromptTemplate
from model.factory import chat_model


class RagSummarizeService(object):
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever()
        self.prompt_text = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self._init_chain()

    def _init_chain(self):
        chain = self.prompt_template | print_prompt | self.model | StrOutputParser()
        return chain

    def retriever_docs(self, query: str) -> list[Document]:
        return self.retriever.invoke(query)

    def rag_summarize(self, query: str) -> str:
        context_docs = self.retriever_docs(query)

        context = ""
        counter = 0
        for doc in context_docs:
            counter += 1
            context += f"【参考资料{counter}】: 参考资料：{doc.page_content} | 参考元数据：{doc.metadata}\n"

        return self.chain.invoke(
            {
                "input": query,
                "context": context,
            }
        )
```

### 8. 数据处理与存储
- **PyYAML** - YAML配置文件解析
- **hashlib** - MD5文件校验（用于去重）
- **SQLite** - Chroma的底层存储引擎
- **CSV** - 外部数据存储（用户使用记录）

**配置加载代码示例：**
```python
import yaml
from utils.path_tool import get_abs_path


def load_rag_config(config_path: str=get_abs_path("config/rag.yml"), encoding: str="utf-8"):
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_chroma_config(config_path: str=get_abs_path("config/chroma.yml"), encoding: str="utf-8"):
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_prompts_config(config_path: str=get_abs_path("config/prompts.yml"), encoding: str="utf-8"):
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_agent_config(config_path: str=get_abs_path("config/agent.yml"), encoding: str="utf-8"):
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


rag_conf = load_rag_config()
chroma_conf = load_chroma_config()
prompts_conf = load_prompts_config()
agent_conf = load_agent_config()
```

### 9. 日志系统
- **Python标准logging模块**
  - 控制台输出（INFO级别）
  - 文件输出（DEBUG级别）
  - 结构化日志格式

**日志处理代码示例：**
```python
import logging
from utils.path_tool import get_abs_path
import os
from datetime import datetime

LOG_ROOT = get_abs_path("logs")
os.makedirs(LOG_ROOT, exist_ok=True)

DEFAULT_LOG_FORMAT = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)


def get_logger(
        name: str = "agent",
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        log_file = None,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(console_handler)

    if not log_file:
        log_file = os.path.join(LOG_ROOT, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(file_handler)

    return logger


logger = get_logger()
```

### 10. Agent中间件机制
- **wrap_tool_call** - 工具调用监控
- **before_model** - 模型调用前钩子
- **dynamic_prompt** - 动态提示词切换

**中间件代码示例：**
```python
from typing import Callable
from utils.prompt_loader import load_system_prompts, load_report_prompts
from langchain.agents import AgentState
from langchain.agents.middleware import wrap_tool_call, before_model, dynamic_prompt, ModelRequest
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import ToolMessage
from langgraph.runtime import Runtime
from langgraph.types import Command
from utils.logger_handler import logger


@wrap_tool_call
def monitor_tool(
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    logger.info(f"[tool monitor]执行工具：{request.tool_call['name']}")
    logger.info(f"[tool monitor]传入参数：{request.tool_call['args']}")

    try:
        result = handler(request)
        logger.info(f"[tool monitor]工具{request.tool_call['name']}调用成功")

        if request.tool_call['name'] == "fill_context_for_report":
            request.runtime.context["report"] = True

        return result
    except Exception as e:
        logger.error(f"工具{request.tool_call['name']}调用失败，原因：{str(e)}")
        raise e


@before_model
def log_before_model(
        state: AgentState,
        runtime: Runtime,
):
    logger.info(f"[log_before_model]即将调用模型，带有{len(state['messages'])}条消息。")
    logger.debug(f"[log_before_model]{type(state['messages'][-1]).__name__} | {state['messages'][-1].content.strip()}")
    return None


@dynamic_prompt
def report_prompt_switch(request: ModelRequest):
    is_report = request.runtime.context.get("report", False)
    if is_report:
        return load_report_prompts()

    return load_system_prompts()
```

### 11. 配置管理
- **YAML配置文件**
  - `agent.yml` - Agent配置
  - `rag.yml` - RAG模型配置
  - `chroma.yml` - 向量数据库配置
  - `prompts.yml` - 提示词路径配置

**配置文件示例：**

`config/rag.yml`:
```yaml
chat_model_name: qwen3-max
embedding_model_name: text-embedding-v4
```

`config/chroma.yml`:
```yaml
collection_name: agent
persist_directory: chroma_db
k: 3
data_path: data
md5_hex_store: md5.text
allow_knowledge_file_type: ["txt", "pdf"]

chunk_size: 200
chunk_overlap: 20
separators: ["\n\n", "\n", ".", "!", "?", "。", "！", "？", " ", ""]
```

`config/agent.yml`:
```yaml
external_data_path: data/external/records.csv
```

### 12. 工具函数
- 自定义工具集：
  - `rag_summarize` - RAG检索总结
  - `get_weather` - 天气查询
  - `get_user_location` - 用户位置
  - `get_user_id` - 用户ID获取
  - `get_current_month` - 当前月份
  - `fetch_external_data` - 外部数据查询
  - `fill_context_for_report` - 报告上下文填充

**工具代码示例：**
```python
import os
from utils.logger_handler import logger
from langchain_core.tools import tool
from rag.rag_service import RagSummarizeService
import random
from utils.config_handler import agent_conf
from utils.path_tool import get_abs_path

rag = RagSummarizeService()

user_ids = ["1001", "1002", "1003", "1004", "1005", "1006", "1007", "1008", "1009", "1010",]
month_arr = ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06",
             "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12", ]

external_data = {}


@tool(description="从向量存储中检索参考资料")
def rag_summarize(query: str) -> str:
    return rag.rag_summarize(query)


@tool(description="获取指定城市的天气，以消息字符串的形式返回")
def get_weather(city: str) -> str:
    return f"城市{city}天气为晴天，气温26摄氏度，空气湿度50%，南风1级，AQI21，最近6小时降雨概率极低"


@tool(description="获取用户所在城市的名称，以纯字符串形式返回")
def get_user_location() -> str:
    return random.choice(["深圳", "合肥", "杭州"])


@tool(description="获取用户的ID，以纯字符串形式返回")
def get_user_id() -> str:
    return random.choice(user_ids)


@tool(description="获取当前月份，以纯字符串形式返回")
def get_current_month() -> str:
    return random.choice(month_arr)


@tool(description="从外部系统中获取指定用户在指定月份的使用记录，以纯字符串形式返回， 如果未检索到返回空字符串")
def fetch_external_data(user_id: str, month: str) -> str:
    generate_external_data()

    try:
        return external_data[user_id][month]
    except KeyError:
        logger.warning(f"[fetch_external_data]未能检索到用户：{user_id}在{month}的使用记录数据")
        return ""


@tool(description="无入参，无返回值，调用后触发中间件自动为报告生成的场景动态注入上下文信息，为后续提示词切换提供上下文信息")
def fill_context_for_report():
    return "fill_context_for_report已调用"
```

### 13. 文件格式支持
- **PDF** - 扫地机器人手册
- **TXT** - 知识库文档
- **CSV** - 用户使用记录

## 项目结构

```
项目根目录/
├── .idea/                          # PyCharm配置
├── agent/                          # Agent智能体模块
│   ├── __pycache__/
│   ├── chroma_db/                  # 向量数据库
│   ├── tools/                      # 工具和中间件
│   │   ├── agent_tools.py          # 工具函数
│   │   └── middleware.py           # 中间件
│   └── react_agent.py              # React Agent实现
├── chroma_db/                      # 向量数据库存储
├── config/                         # 配置文件
│   ├── agent.yml
│   ├── chroma.yml
│   ├── prompts.yml
│   └── rag.yml
├── data/                           # 数据目录
│   ├── external/                   # 外部数据
│   │   └── records.csv
│   ├── 扫地机器人100问.pdf
│   ├── 扫地机器人100问2.txt
│   ├── 扫拖一体机器人100问.txt
│   ├── 故障排除.txt
│   ├── 维护保养.txt
│   └── 选购指南.txt
├── logs/                           # 日志文件
│   ├── agent_20260125.log
│   └── agent_20260126.log
├── model/                          # 模型工厂
│   ├── __pycache__/
│   └── factory.py
├── prompts/                        # 提示词模板
│   ├── main_prompt.txt
│   ├── rag_summarize.txt
│   └── report_prompt.txt
├── rag/                            # RAG服务模块
│   ├── __pycache__/
│   ├── chroma_db/
│   ├── rag_service.py
│   └── vector_store.py
├── utils/                          # 工具函数
│   ├── __pycache__/
│   ├── config_handler.py           # 配置处理
│   ├── file_handler.py             # 文件处理
│   ├── logger_handler.py           # 日志处理
│   ├── path_tool.py                # 路径工具
│   └── prompt_loader.py            # 提示词加载
├── app.py                          # Streamlit应用入口
└── md5.text                        # 文件MD5记录
```

## 架构特点

### 1. RAG架构
- 检索增强生成，结合向量检索和LLM生成
- 支持PDF和TXT文档的知识库构建
- 自动文档分块和向量化

### 2. Agent架构
- 智能体工具调用，支持多工具协作
- 基于LangChain的Agent框架
- 支持流式输出

### 3. 流式输出
- 实时响应，提升用户体验
- 逐字符显示效果

### 4. 中间件机制
- 灵活的钩子系统，支持监控和动态配置
- 工具调用监控
- 模型调用前日志
- 动态提示词切换

### 5. 动态提示词
- 根据场景自动切换系统提示词
- 支持常规问答和报告生成两种模式

### 6. 文件去重
- MD5校验避免重复加载知识库
- 提高系统效率

## 技术亮点

1. **模块化设计** - 清晰的代码结构，易于维护和扩展
2. **配置驱动** - 使用YAML配置文件，灵活调整参数
3. **完善的日志系统** - 支持多级别日志，便于调试和监控
4. **中间件机制** - 灵活的钩子系统，支持自定义扩展
5. **流式响应** - 实时输出，提升用户体验
6. **文件去重** - MD5校验，避免重复处理
7. **多格式支持** - 支持PDF、TXT、CSV等多种文件格式
8. **向量检索** - 基于Chroma的高效向量搜索

## 应用场景

- 智能客服系统
- 知识问答系统
- 文档检索系统
- 用户报告生成
- 多轮对话系统

## 总结

这是一个典型的**现代AI应用架构**，结合了RAG的知识检索能力和Agent的工具调用能力，非常适合构建智能客服系统。项目采用了模块化设计，代码结构清晰，易于维护和扩展。通过LangChain框架的强大功能，实现了从文档处理、向量化存储、智能检索到自然语言生成的完整流程。
