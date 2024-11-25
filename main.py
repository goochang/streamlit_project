import streamlit as st
from streamlit_chat import message
from openai import OpenAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

print()
print()
print()
print()

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "active" not in st.session_state:
    st.session_state["active"] = ""
if "side_data" not in st.session_state:
    st.session_state["side_data"] = []

st.title("Chat bot test")

placeholder = st.empty()

now_dir = os.getcwd()
def init():
    # 대화내역 불러오기 위한 데이터
    if os.path.isdir(now_dir + "\History"):
        prompt_file = os.listdir(now_dir + "\History")

        prompt_file = sorted(prompt_file, key=lambda x: int(x.split('.')[0].replace("history", "")), reverse=True)

        if len(prompt_file) > 0 and len(st.session_state.side_data) == 0:
            for file in prompt_file:
                with open(now_dir + "/History/" + file, 'r', encoding='UTF8') as f:
                    json_data = json.load(f)
                    side_title = json_data[0]["content"][0:20]
                    st.session_state.side_data.append({side_title:file})
                    
def split_long_text(text, line_length=80):
    print(text)
    return [text[i:i+line_length] for i in range(0, len(text), line_length)]

def render_sidebar():
    with st.sidebar:
        st.title('Chat Rooms')
        # sidebar_placeholder = st.sidebar.empty() # 사이드바에 다른 요소 추가시키기 위함        
        # print(len(st.session_state.side_data))
        print(st.session_state)
        for i, room in enumerate(st.session_state.side_data):
            print("room",room.items())
            for room_name, file_name in room.items():
                button_key = f"{room_name}_{file_name}{i}"  
                if st.button(room_name, key=button_key):  # 각 대화방 이름을 버튼으로 출력
                    print("btn", button_key)
                    # placeholder.empty()
                    st.session_state["messages"] = []
                    st.session_state["active"] = now_dir + "/History/" + file_name
                    with placeholder.container():
                        with open(os.path.join(now_dir, "History", file_name), 'r', encoding='UTF8') as f:
                            json_data = json.load(f)
                            for message in json_data:
                                # with st.chat_message(message["role"]):
                                #     st.write(message["content"])
                                st.session_state.messages.append({"role":message["role"], "content":message["content"]})
                                    

def click_event(data):
    print(data)
def session_save(data):
    now_dir = os.getcwd()
    history_dir = now_dir + "/History/"
    if os.path.isdir(history_dir):
        # prompt 폴더에 파일이 있는지 확인
        prompt_file = os.listdir(history_dir)
        file_cnt = len(prompt_file)+1

        file_name = "history" + str(file_cnt) + ".json"

        active = st.session_state.active
        print(active == "", active)
        # 첫 질문 - session_state 값 없음 - dump로 생성
        if active == "":
            print("file", history_dir + file_name)
            with open(history_dir + file_name, 'w', encoding='UTF8') as f:
                json.dump([data], f)

                room_name = data["content"][0:20]
                st.session_state["active"] = f.name
                st.session_state.side_data.insert(0,{room_name:file_name})

                # st.sidebar.rerun()
                # with sidebar_placeholder.container():
                #     button_key = f"{room_name}_{file_name}{len(st.session_state.side_data)}"  
                    
                #     st.button(room_name, key=button_key, on_click=click_event(button_key))

                    # if st.button(room_name, key=button_key):  # 각 대화방 이름을 버튼으로 출력
                    #     print("new")
                    #     # st.session_state["messages"] = [] # 중복메시지 출력되는 부분 해결을 위함
                    #     st.session_state["active"] = file_name
                    #     placeholder.empty()
                    #     with placeholder.container():
                    #         with open(os.path.join(now_dir, "History", file_name), 'r', encoding='UTF8') as f:
                    #             json_data = json.load(f)
                    #             for message in json_data:
                    #                 with st.chat_message(message["role"]):
                    #                     st.write(message["content"])
        # 두번째는 - session_state 값 있음 - update
        elif os.path.isfile(active):
            print("file", active)
            with open(active, 'r', encoding='UTF8') as f:
                try:
                    # 기존 대화 불러오기
                    json_data = json.load(f)
                    if not isinstance(json_data, list):
                        json_data = []  # 파일에 리스트가 없으면 초기화
                except json.JSONDecodeError:
                    json_data = []  # 파일이 비어있으면 초기화
                    
                json_data.append(data)
            with open(active, 'w', encoding='UTF8') as f:
                json.dump(json_data, f)

# print(st.session_state)




# 사이드바

# if st.session_state.active:
    # st.write(f"선택된 대화방: {st.session_state.active}")
    # 여기에서 선택된 파일의 내용을 로드하여 화면에 표시합니다.
# else:
    # st.write("대화방을 선택하세요.")
    
# 메세지 추가시 화면에 표시

init()
render_sidebar()

for message in st.session_state["messages"]:
    print("mesg", message)
    with st.chat_message(message["role"]):
        st.write(message["content"])


# 입력시 입력값과 결과값 st.session_state["messages"]에 추가
if prompt := st.chat_input("Say something"):
    data = {"role":"user", "content":prompt}
    st.session_state.messages.append(data)

    session_save(data)
    print(data)

    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model = st.session_state["openai_model"],
            messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream = True,
        )
        response = st.write_stream(stream)

        data = {"role":"assistant", "content":response}
        st.session_state.messages.append({"role":"assistant", "content":response})
        
        session_save(data)
        print(response)