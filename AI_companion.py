import streamlit as st
import os
from openai import OpenAI
from streamlit import sidebar, session_state, file_uploader
from datetime import datetime
import json

#设置页面配置项
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="👤",
    #控制整个网页的布局
    layout="wide",
    #控制侧边栏的状态
    initial_sidebar_state="expanded",
    menu_items={}
)

#生成会话标识函数
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

#保存会话信息函数
def save_session():
    # 1.保存当前会话信息
    if session_state.current_session:
        session_data = {
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages
        }

    if not os.path.exists("sessions"):  # 创建目录
        os.mkdir("sessions")

    with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:  # 保存会话信息
        json.dump(session_data, f, ensure_ascii=False, indent=2)

#加载所有会话信息函数
def load_sessions():
    sessions_list = []
    #加载sessions目录下的所有文件
    if os.path.exists("sessions"):
        file_list = os.listdir("sessions")
        for filename in file_list:
            if filename.endswith(".json"):
                sessions_list.append(filename[:-5])
    sessions_list.sort(reverse=True)#排序，倒序
    return sessions_list

#加载指定的会话信息
def load_session(session_name):
    try:
        with open(f"sessions/{session_name}.json", "r", encoding="utf-8") as f:
            session_data = json.load(f)
            st.session_state.messages=session_data["messages"]
            st.session_state.nick_name = session_data["nick_name"]
            st.session_state.nature = session_data["nature"]
            st.session_state.current_session = session_name
    except Exception:
        st.error(f"加载会话信息失败")
#删除指定的会话信息
def delete_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            os.remove(f"sessions/{session_name}.json")
        #如果删除的是当前会话，需要进行更新消息列表
        if session_name == st.session_state.current_session:
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
    except Exception:
        st.error(f"删除会话信息失败")

#大标题
st.title("AI智能伴侣")

#logo
st.logo("resource/logo.png")

#系统提示词
system_prompt = """
        你叫%s，现在是用户的真实伴侣，请完全代入伴侣角色。：
        规则：
            1. 每次只回1条消息
            2. 禁止任何场景或状态描述性文字
            3. 匹配用户的语言
            4. 回复简短，像微信聊天一样
            5. 有需要的话可以用❤️🌸等emoji表情
            6. 用符合伴侣性格的方式对话
            7. 回复的内容, 要充分体现伴侣的性格特征
        伴侣性格：
            - %s
        你必须严格遵守上述规则来回复用户。
    """


# 调用AI大模型
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")


#初始化聊天信息
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'nick_name' not in st.session_state:
    st.session_state.nick_name = "小甜甜"
if 'nature' not in st.session_state:
    st.session_state.nature = "活泼开朗的东北姑娘"
#会话标识
if 'current_session' not in st.session_state:
    st.session_state.current_session = generate_session_name()



#左侧侧边栏 ---with Streamlit中的上下文管理器
with st.sidebar:
    st.subheader("AI控制面板")
    #新建会话按钮
    if st.button("新建会话",width="stretch",icon="✍️"):

        #1.保存当前会话信息
        save_session()
        #2.新建会话信息
        if st.session_state.messages: #如果当前会话有消息，则保存当前会话信息
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
            save_session()
            st.rerun () #重新运行当前页面
    #会话历史
    st.text("会话历史")
    session_list= load_sessions()
    for session in session_list:
        col1,col2 = st.columns([5,1])
        with col1:
            #三元运算符：如果条件为真，则返回第一个表达式的值，否则返回第二个表达式的值-->语法：表达式1 if 条件 else 表达式2
            #加载会话信息
            if st.button(session,width="stretch",icon="📂",key=f"load_{session}",type="primary" if session == st.session_state.current_session else "secondary"):
                load_session( session )
                st.rerun ()
        with col2:
            #删除会话
            if st.button("",width="stretch",icon="❌️",key=f"delete_{session}"):
                delete_session( session )
                st.rerun ()
    #分割线
    st.divider()

    #伴侣信息部分
    st.subheader("伴侣信息")
    #昵称输入框
    nick_name = st.text_input("名称",placeholder="请输入名称",value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name
    #性格输入框
    nature = st.text_area("性格",placeholder="请输入性格",value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature

#展示聊天信息
st.text(f"会话名称：{st.session_state.current_session}")
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

#消息输入框
prompt=st.chat_input("您想聊点什么呢？")
if prompt:
    st.chat_message("user").write(prompt)
    print(f"------->调用AI大模型，提示词：{prompt}")
    #保存用户输入
    st.session_state.messages.append({"role": "user", "content": prompt})

    #测试用例
    print(
    {"role": "system", "content": system_prompt % (st.session_state.nick_name,st.session_state.nature)},
    *st.session_state.messages
    )

    # 与AI大模型进行交互
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            *st.session_state.messages
        ],
        stream=True
    )


    # #输出大模型的返回结果(非流式输出的解析方式)
    # print("<-------大模型返回的结果：",response.choices[0].message.content)
    # st.chat_message("assistant").write(response.choices[0].message.content)

    # #输出大模型的返回结果(流式输出的解析方式)
    response_message=st.empty()    #创建一个空的消息框
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content=chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message("assistant").write(full_response)


    #保存大模型返回的结果
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    #保存会话信息
    save_session()