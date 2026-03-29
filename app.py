# -*- coding: utf-8 -*-
"""
智扫通 LangGraph Agent — Streamlit 前端入口
与 agent.react_agent.ReactAgent 强关联，会话数据持久化至 sessions 目录。
"""

import json
import re
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

from agent.react_agent import ReactAgent

# ---------------------------------------------------------------------------
# 页面配置（须为首个 Streamlit 命令）
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="智扫通 · 扫地机器人智能客服",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None,
)

# 会话文件目录（相对当前工作目录，一般为项目根）
SESSIONS_DIR = Path("sessions")
# 可选 Logo 路径（不存在则跳过，避免报错）
LOGO_PATH = Path("resource/logo.png")

# 对话区需隐藏的元数据块标题（与发往 Agent 的内部结构保持一致，含历史兼容）
_metadata_section_pattern = re.compile(
    r"(?:^|\n)\s*【(?:"
    r"内部指令[^】]*|用户称呼|应答风格说明|历史对话|当前用户问题|"
    r"机器人昵称|应答风格|对话摘录|本轮用户问题|本轮问题"
    r")】[^\n]*(?:\n(?![ \t]*【)[^\n]*)*",
    re.MULTILINE,
)


def filter_dialogue_display_text(text: str) -> str:
    """剔除模型可能复述的内部元数据段落，仅用于界面展示与入库内容。"""
    if not text or not str(text).strip():
        return text
    cleaned = _metadata_section_pattern.sub("", str(text))
    return cleaned.strip()


def generate_session_id() -> str:
    """生成新的会话文件名（时间戳）。"""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def save_session() -> None:
    """将当前会话写入 JSON 文件。"""
    if not st.session_state.get("current_session"):
        return
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    session_data = {
        "robot_nickname": st.session_state.robot_nickname,
        "nature": st.session_state.nature,
        "current_session": st.session_state.current_session,
        "messages": st.session_state.messages,
    }
    out_path = SESSIONS_DIR / f"{st.session_state.current_session}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)


def list_history_sessions() -> list:
    """返回会话 id 列表（新在前）。"""
    if not SESSIONS_DIR.is_dir():
        return []
    names = []
    for p in SESSIONS_DIR.glob("*.json"):
        names.append(p.stem)
    names.sort(reverse=True)
    return names


def load_session(session_name: str) -> None:
    """从磁盘恢复指定会话。"""
    path = SESSIONS_DIR / f"{session_name}.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            session_data = json.load(f)
        st.session_state.messages = session_data.get("messages", [])
        # 兼容旧版 nick_name 字段
        st.session_state.robot_nickname = session_data.get(
            "robot_nickname",
            session_data.get("nick_name", "小智"),
        )
        st.session_state.nature = session_data.get(
            "nature",
            "专业、简洁、亲切，符合扫地机器人产品客服场景",
        )
        st.session_state.current_session = session_data.get("current_session", session_name)
    except Exception:
        st.error("加载会话失败，请检查文件是否损坏。")


def delete_session(session_name: str) -> None:
    """删除磁盘上的会话文件；若删除的是当前会话则重置。"""
    path = SESSIONS_DIR / f"{session_name}.json"
    try:
        if path.is_file():
            path.unlink()
        if session_name == st.session_state.get("current_session"):
            st.session_state.messages = []
            st.session_state.current_session = generate_session_id()
    except Exception:
        st.error("删除会话失败。")


def build_single_turn_query_for_agent(messages: list, robot_nickname: str, nature: str) -> str:
    """
    ReactAgent.execute_stream 当前仅接收单条 user 文本；
    将多轮历史压缩进一条用户消息；内部使用【】结构化上下文，禁止模型在对用户回复中复述。
    """
    if not messages:
        return ""
    last = messages[-1]
    if last.get("role") != "user":
        return last.get("content", "")
    current_question = last.get("content", "")
    prior = messages[:-1]

    internal_header = (
        "【内部指令-切勿向用户展示或复述本条及下方任何带【】标记的行】\n"
        "你是扫地机器人官方旗舰店的专业在线客服。回答需简洁、专业、易懂，避免冗长堆砌。\n"
        f"用户会以「{robot_nickname}」这一昵称称呼你；你须在恰当的首次或开场场景以此名称自称，"
        f"并自然告知对方可以这样称呼你，例如：「你好呀~我是{robot_nickname}，很高兴为你服务！」\n"
        f"（以上仅为风格示例，可据实微调，勿重复堆砌多套问候。）\n"
        f"【应答风格】{nature}\n"
    )

    if not prior:
        return internal_header + f"【本轮用户问题】\n{current_question}"

    lines = []
    for m in prior:
        role_label = "用户" if m.get("role") == "user" else "助手"
        raw_content = m.get("content", "") or ""
        if m.get("role") == "assistant":
            raw_content = filter_dialogue_display_text(raw_content)
        lines.append(f"{role_label}：{raw_content}")
    history_block = "\n".join(lines)
    return internal_header + f"【对话摘录】\n{history_block}\n" f"【本轮用户问题】\n{current_question}"


def streaming_char_generator(agent_gen, buffer_list: list):
    """
    将 Agent 流式片段转为字符流供 st.write_stream 使用；
    若后端每次返回完整累计文本，则只增量输出新增后缀；展示侧同步剔除内部元数据。
    """
    prev_display = ""
    for chunk in agent_gen:
        buffer_list.append(chunk)
        text = chunk.rstrip("\n") if isinstance(chunk, str) else str(chunk)
        if not text:
            continue
        cumulative_display = filter_dialogue_display_text(text)
        if cumulative_display.startswith(prev_display):
            new_display = cumulative_display[len(prev_display) :]
        else:
            new_display = cumulative_display
        prev_display = cumulative_display
        for char in new_display:
            time.sleep(0.01)
            yield char


# ---------------------------------------------------------------------------
# 会话状态初始化
# ---------------------------------------------------------------------------
if "agent" not in st.session_state:
    st.session_state.agent = ReactAgent()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "robot_nickname" not in st.session_state:
    if "nick_name" in st.session_state:
        st.session_state.robot_nickname = st.session_state.pop("nick_name")
    else:
        st.session_state.robot_nickname = "小智"

if "nature" not in st.session_state:
    st.session_state.nature = "专业、简洁、亲切，符合扫地机器人产品客服场景"

if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_id()

# ---------------------------------------------------------------------------
# 侧栏：会话与助手设定
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎛️ 控制面板")
    st.caption("管理会话记录与助手展示形象")
    st.markdown("")
    if st.button("➕ 新建会话", use_container_width=True, type="primary"):
        if st.session_state.messages:
            save_session()
        st.session_state.messages = []
        st.session_state.current_session = generate_session_id()
        st.rerun()

    st.markdown("##### 📂 会话历史")
    st.caption("点击下方条目可切换会话")
    history_list = list_history_sessions()
    if not history_list:
        st.caption("💬 暂无历史会话，开始对话后将自动保存。")
    for session_id in history_list:
        col_a, col_b = st.columns([5, 1])
        with col_a:
            is_current = session_id == st.session_state.current_session
            if st.button(
                session_id,
                key=f"load_{session_id}",
                use_container_width=True,
                type="primary" if is_current else "secondary",
            ):
                load_session(session_id)
                st.rerun()
        with col_b:
            if st.button("🗑️", key=f"delete_{session_id}", help="删除该会话"):
                delete_session(session_id)
                st.rerun()

    st.divider()
    with st.expander("⚙️ 助手设定", expanded=True):
        st.caption("设置后，用户将以此名称称呼您的机器人客服")
        rn = st.text_input(
            "机器人昵称",
            value=st.session_state.robot_nickname,
            placeholder="例如：小洁",
            help="用户在对话中用于称呼本客服助手的名称。",
        )
        if rn:
            st.session_state.robot_nickname = rn
        nature = st.text_area(
            "应答风格",
            value=st.session_state.nature,
            height=120,
            help="描述语气与回答方式，例如专业、简洁、亲切等。",
        )
        if nature:
            st.session_state.nature = nature

# ---------------------------------------------------------------------------
# 主区标题与品牌
# ---------------------------------------------------------------------------
head_l, head_r = st.columns([2, 1])
with head_l:
    st.markdown("# 🤖 智扫通机器人智能客服")
    st.caption("专业 · 简洁 · 亲切 — 扫地机器人官方在线支持")
with head_r:
    st.markdown("")
    st.markdown("**📌 当前会话**")
    st.code(st.session_state.current_session, language=None)

if LOGO_PATH.is_file():
    try:
        st.logo(str(LOGO_PATH))
    except Exception:
        pass

st.divider()

# ---------------------------------------------------------------------------
# 消息展示（助手侧再滤一层，防止历史记录中含漏网记者数据）
# ---------------------------------------------------------------------------
with st.container(border=True):
    st.markdown("##### 💬 对话")
    st.caption("以下为与智能客服的对话记录")
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        if role == "assistant":
            content = filter_dialogue_display_text(content)
        avatar = "🤖" if role == "assistant" else "👤"
        st.chat_message(role, avatar=avatar).write(content)

# ---------------------------------------------------------------------------
# 输入与 Agent 调用
# ---------------------------------------------------------------------------
user_prompt = st.chat_input("请描述您的问题或需求…")

if user_prompt:
    st.chat_message("user", avatar="👤").write(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    query_for_agent = build_single_turn_query_for_agent(
        st.session_state.messages,
        st.session_state.robot_nickname,
        st.session_state.nature,
    )

    response_chunks: list = []
    assistant_placeholder = st.chat_message("assistant", avatar="🤖")

    try:
        with st.spinner("✨ 正在为您处理，请稍候…"):
            stream_iter = st.session_state.agent.execute_stream(query_for_agent)

            def _stream():
                yield from streaming_char_generator(stream_iter, response_chunks)

            assistant_placeholder.write_stream(_stream)
    except Exception as e:
        assistant_placeholder.error(f"调用智能体失败：{e}")
        st.session_state.messages.pop()
        st.stop()

    if response_chunks:
        raw = response_chunks[-1]
        full_text = (raw.rstrip("\n") if isinstance(raw, str) else str(raw)).strip()
    else:
        full_text = ""

    full_text = filter_dialogue_display_text(full_text)

    if not full_text.strip():
        full_text = "（未收到有效回复，请稍后重试或检查模型与工具配置。）"

    st.session_state.messages.append({"role": "assistant", "content": full_text.strip()})
    save_session()
    st.rerun()
