import streamlit as st
from openai import OpenAI
import urllib.request
from PIL import Image
import json

# API 키와 클라이언트 설정
st.session_state.key = st.text_input("key", value=st.session_state.get("key", ""), type="password")
st.session_state.client = OpenAI(api_key=st.session_state.key)

st.header("챗봇")

@st.cache_data
def generate_image(prompt):
    # 주어진 프롬프트로 이미지를 생성하고 반환
    client = OpenAI(api_key=st.session_state.key)
    response = client.images.generate(model="dall-e-3", prompt=prompt)
    image_url = response.data[0].url
    urllib.request.urlretrieve(image_url, 'img.png')
    img = Image.open("img.png")
    return img

def display_message(role, content):
    with st.chat_message(role):
        if isinstance(content, str):
            st.markdown(content)
        else:
            st.image(content, use_column_width=True)

def clear_chat():
    if "messages" in st.session_state:
        del st.session_state.messages
    if "thread" in st.session_state:
        st.session_state.client.beta.threads.delete(st.session_state.thread.id)
        del st.session_state.thread

def exit_chat():
    if "messages" in st.session_state:
        del st.session_state.messages
    if "thread" in st.session_state:
        st.session_state.client.beta.threads.delete(st.session_state.thread.id)
        del st.session_state.thread
    if "assistant" in st.session_state:
        st.session_state.client.beta.assistants.delete(st.session_state.assistant.id)
        del st.session_state.assistant

def initialize_assistant():
    if "assistant" not in st.session_state:
        st.session_state.assistant = st.session_state.client.beta.assistants.create(
            instructions="챗봇입니다",
            model="gpt-4o",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "generate_image",
                        "description": "dall-e를 이용해 받은 프롬포트를 바탕으로 그림을 그린다.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "prompt": {"type": "string", "description": "프롬포트"}
                            }
                        }
                    }
                },
                {"type": "code_interpreter"}
            ]
        )

def handle_prompt(prompt):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    st.session_state.thread = st.session_state.client.beta.threads.create(
        messages=[{"role": "user", "content": prompt}]
    )

    run = st.session_state.client.beta.threads.runs.create_and_poll(
        thread_id=st.session_state.thread.id,
        assistant_id=st.session_state.assistant.id
    )

    run_check = st.session_state.client.beta.threads.runs.retrieve(
        thread_id=st.session_state.thread.id,
        run_id=run.id
    )

    if run_check.status == 'requires_action':
        handle_tool_calls(run_check.required_action.submit_tool_outputs.tool_calls, run)
    else:
        display_response(run)

def handle_tool_calls(tool_calls, run):
    tool_outputs = []
    for tool in tool_calls:
        func_name = tool.function.name
        kwargs = json.loads(tool.function.arguments)
        output = generate_image(**kwargs)
        tool_outputs.append({"tool_call_id": tool.id, "output": str(output)})

    st.session_state.client.beta.threads.runs.submit_tool_outputs(
        thread_id=st.session_state.thread.id,
        run_id=run.id,
        tool_outputs=tool_outputs
    )

def display_response(run):
    thread_messages = st.session_state.client.beta.threads.messages.list(
        st.session_state.thread.id, run_id=run.id)
    response = f"Echo: {thread_messages.data[0].content[0].text.value}"

    display_message("assistant", response)
    st.session_state.messages.append({"role": "assistant", "content": response})

if st.button("Clear"):
    clear_chat()

if st.button("대화창 나가기"):
    exit_chat()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    display_message(msg["role"], msg["content"])

if prompt := st.chat_input("What is up?"):
    initialize_assistant()
    handle_prompt(prompt)