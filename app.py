import streamlit as st
# import torch

# # Clear GPU memory
# torch.cuda.empty_cache()

from llm_chains import load_normal_chain
from langchain.memory import StreamlitChatMessageHistory
# from streamlit_mic_recorder import mic_recorder
from utils import save_chat_history_json, get_timestamp, load_chat_history_json
import yaml
import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Use environment variables for server configuration
ollama_server_host = os.environ.get("OLLAMA_SERVER_HOST", "localhost")
ollama_server_port = os.environ.get("OLLAMA_SERVER_PORT", "11434")

# ... (rest of the code remains the same)

# Replace 'localhost' and '11434' with environment variables
ollama_server_host = os.environ.get("OLLAMA_SERVER_HOST", "localhost")
ollama_server_port = os.environ.get("OLLAMA_SERVER_PORT", "11434")

def load_chain(chat_history):
    return load_normal_chain(chat_history)

def clear_input_field():
    st.session_state.user_question = st.session_state.user_input
    st.session_state.user_input = ""

def set_send_input():
    st.session_state.send_input = True
    clear_input_field()

def track_index():
    st.session_state.session_index_tracker=st.session_state.session_key

def save_chat_history():
    if st.session_state.history != []:
        if st.session_state.session_key == "new_session":
            st.session_state.new_session_key = get_timestamp() + ".json"
            save_chat_history_json(st.session_state.history, config["chat_history_path"] + st.session_state.new_session_key)
        else:
            save_chat_history_json(st.session_state.history, config["chat_history_path"] + st.session_state.session_key)

def main():
    st.title("AI Chat App")
    chat_container = st.container()
    st.sidebar.title("Chat Sessions")
    chat_sessions = ["new_session"] + os.listdir(config["chat_history_path"])
    print(chat_sessions)
    if "send_input" not in st.session_state:
        st.session_state.session_key = "new_session"
        st.session_state.send_input = False
        st.session_state.user_question = ""
        st.session_state.new_session_key = None
        st.session_state.session_index_tracker = "new_session"
    if st.session_state.session_key == "new_session" and st.session_state.new_session_key != None:
        st.session_state.session_index_tracker = st.session_state.new_session_key
        st.session_state.new_session_key = None

    index = chat_sessions.index(st.session_state.session_index_tracker)
    st.sidebar.selectbox("Select a chat session", chat_sessions, key="session_key",index=index,on_change=track_index)


    if st.session_state.session_key != "new_session":
        st.session_state.history = load_chat_history_json(config["chat_history_path"] + st.session_state.session_key)
    else:
        st.session_state.history = []


    chat_history=StreamlitChatMessageHistory(key="history")
    llm_chain=load_chain(chat_history)   

    user_input = st.text_input("Type your message here", key="user_input", on_change=set_send_input)
    # voice_recording_column,send_button_column=st.columns(2)
    # with voice_recording_column:
    #     voice_recording=mic_recorder(start_prompt="Start recording",stop_prompt="Stop recording", just_once=True)
    # with send_button_column:
    send_button = st.button("Send", key="send_button", on_click=clear_input_field)

    # print(voice) 
    # send_button=st.button("Send",key="send_button")

    if send_button or st.session_state.send_input:
        if st.session_state.user_question!="":
            with chat_container:
                st.chat_message("User").write(st.session_state.user_question)
                llm_response=llm_chain.run(st.session_state.user_question)
                # st.chat_message("ai").write(llm_response)
                st.session_state.user_question=""


    if send_button or st.session_state.send_input:
        if st.session_state.user_question != "":
            try:
                with chat_container:
                    st.chat_message("User").write(st.session_state.user_question)

                    # Print Ollama server host and port before making the request
                    print(f"Ollama Server Host: {ollama_server_host}, Ollama Server Port: {ollama_server_port}")

                    llm_response = llm_chain.run(st.session_state.user_question)
                    st.session_state.user_question = ""
            except requests.exceptions.ConnectionError as e:
                st.error(f"Error connecting to the server: {e}. Make sure the Ollama server is running and accessible.")

    if chat_history.messages != []:
        with chat_container:
            st.write("Chat History:")
            for message in chat_history.messages:
                st.chat_message(message.type).write(message.content)

    save_chat_history()

if __name__ == "__main__":
    main()