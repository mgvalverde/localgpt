"""
Local GPT

Streamlit version for ChatGPT
It allow the use through the API

"""

import logging
import os

import langchain
import streamlit as st
from langchain.cache import InMemoryCache
from langchain.callbacks import StreamlitCallbackHandler

from localgpt.conversation.builder import (
    get_chat_assistant,
    rewrite_conversation,
)
from localgpt.memory.sqlite import SQLEnhancedChatMessageHistory
from localgpt.utils import (
    generate_uuid,
    reset_conversation,
    update_load_boolean_callback,
    preprocess_title,
    resolve_path,
    delete_conversation
)

langchain.llm_cache = InMemoryCache()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TODO: take those to a config file
openai_model_options = ["gpt-4-1106-preview", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"]
agent_tools = ["llm-math"]
db_path = "~/.localgpt/chat_history.db"
model_temperature = 0
play_streaming = True
db_history_table_name = "message_store"
title_default_len = 12
st.set_page_config(page_title="Local GPT")

#
db_resolved_path = resolve_path(db_path, mkdir=True)
db_connection_string = fr"sqlite:///{db_resolved_path}"

# Changes of db_connection_string are applied when reloading the page
if "db_connection_string" not in st.session_state:
    st.session_state.db_connection_string = db_connection_string

if "ongoing_conversation_id" not in st.session_state:
    st.session_state.ongoing_conversation_id = generate_uuid()

if "do_delete_conversation" not in st.session_state:
    st.session_state.do_delete_conversation = 0

with st.sidebar:
    st.title("⚙️ Configuration")
    if "OPENAI_API_KEY" in os.environ:
        st.text("🔑 OpenAI API Key found")
        openai_api_key = os.getenv("OPENAI_API_KEY")
    else:
        openai_api_key = st.text_input(
            "OpenAI API Key", key="chatbot_api_key", type="password"
        )

    st.selectbox(
        "Set the backend model",
        key="openai_model",
        options=openai_model_options,
        index=0,
    )

    model_temperature = st.slider('Model temperature', 0.0, 1.0, 0.01)

    st.text("⛓ Chain Mode")

    # History
    for _ in range(12):
        st.text(" ") ## add extra expace

    message_history = SQLEnhancedChatMessageHistory(
        session_id=st.session_state.ongoing_conversation_id,
        connection_string=st.session_state.db_connection_string,
        table_name=db_history_table_name
    )
    conversation_mapping = message_history.list_chats()

    selected_conversation = st.selectbox(
        "📖 Conversation History",
        conversation_mapping.keys(),
        key="selected_conversation",
        format_func=lambda x: conversation_mapping[x]
    )

    condition_load_callback = bool(len(conversation_mapping))

    load_conversation_button = st.button(
        "Load Conversation",
        key="load_conversation_button",
        use_container_width=True,
        on_click=lambda: update_load_boolean_callback(condition_load_callback,
                                                      "ongoing_conversation_id",
                                                      st.session_state.selected_conversation
                                                      ),
    )
    new_conversation_button = st.button(
        "New Conversation",
        key="new_conversation_button",
        use_container_width=True,
        on_click=reset_conversation,
    )
    # deletion section
    col_del_conv, col_del_conf = st.columns(2)

    with col_del_conv:
        delete_conversation_button = st.button(
            "Delete\nConversation",
            use_container_width=True,
            on_click=lambda: update_load_boolean_callback(
                cond=True,
                key="do_delete_conversation",
                value=True
            )
        )

    with col_del_conf:
        if st.session_state.do_delete_conversation:
            conf_delete_conversation_button = st.button(
                "Confirm\nDeletion",
                use_container_width=True,
                on_click=lambda: delete_conversation(
                    selected_conversation,
                    st.session_state.db_connection_string,
                    db_history_table_name
                )
            )
        st.session_state.do_delete_conversation = 0

## main block

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.")
    st.stop()
try:
    st.subheader(conversation_mapping[st.session_state.ongoing_conversation_id])
except KeyError:
    st.subheader("New Conversation")

assistant = get_chat_assistant(
    session_id=st.session_state.ongoing_conversation_id,
    connection_string=st.session_state.db_connection_string,
    api_key=openai_api_key,
    model=st.session_state.openai_model,
    tools=[], # using chains
    table_name=db_history_table_name,
    temperature=model_temperature,
    streaming=play_streaming,
)

container_history = st.container()

rewrite_conversation(messages=message_history.messages,
                     container=container_history,
                     upwards=False,
                     )
if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    container_ephemeral = st.container()
    st_callback = StreamlitCallbackHandler(parent_container=container_ephemeral)
    response = assistant.run(prompt, callbacks=[st_callback])

# Auto title handling
ongoing_conversation_name = message_history \
    .list_chats() \
    .get(st.session_state.ongoing_conversation_id)

if ongoing_conversation_name == "Untitled Conversation" and \
        prompt is not None:
    message_history.upsert_title(title=preprocess_title(prompt, length=title_default_len))
