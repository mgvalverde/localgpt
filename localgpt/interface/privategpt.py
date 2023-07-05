"""
# This is the document title

This is some _markdown_.
"""

import os
import streamlit as st
import langchain
from langchain.callbacks import StreamlitCallbackHandler
from localgpt.memory.tinydb import TinyDBChatMessageHistory
from langchain.cache import InMemoryCache
from localgpt.conversation.conversation import (
    OpenAIChatbotBuilder,
    rewrite_conversation,
    ConversationManager,
)
import logging
import uuid
from streamlit_option_menu import option_menu

langchain.llm_cache = InMemoryCache()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

openai_model_options = ["gpt-3.5-turbo", "gpt-4"]
agent_tools = ["llm-math"]

# container_top = st.container()
# col1, col2 = st.columns(2)
# with container_top:
#     with col1:
#         st.session_state

if "ongoing_conversation_id" not in st.session_state:
    st.session_state.ongoing_conversation_id = uuid.uuid4().hex

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

    st.multiselect(
        "Set the tools for your agent",
        key="agent_tools",
        options=agent_tools,
        # default=agent_tools[0]
    )

    if st.session_state.agent_tools:
        st.text("🚀 Agent Mode")
    else:
        st.text("⛓ Chain Mode")

    with st.sidebar.expander("🛠 API keys for tools", expanded=True):
        st.text("Introduce API keys for tools")


    # History

    def reset_conversation():
        st.session_state.update(ongoing_conversation_id=uuid.uuid4().hex)


    new_conversation_button = st.button(
        "New Conversation",
        key="new_conversation_button",
        use_container_width=True,
        on_click=reset_conversation,
    )

    message_history = TinyDBChatMessageHistory()
    conversation_list = list(message_history.db.tables())

    rev_conversation_list = sorted(conversation_list, reverse=True)
    # if rev_conversation_list:
    #     selected = option_menu(
    #         "Conversation History",
    #         rev_conversation_list,
    #         menu_icon="book",
    #         key="conversation_id",
    #         manual_select=True,
    #     )
    #     if not new_conversation_button:
    #         st.session_state.ongoing_conversation_id = selected
    # if "selected_conversation" not in st.session_state:
    #     st.session_state.selected_conversation =
    # if rev_conversation_list:
    selected_conversation = st.selectbox(
        "📖 Conversation History",
        rev_conversation_list,
        key="selected_conversation",
    )
    def update_load_boolean_callback(x:bool):
        if x:
            st.session_state.update(ongoing_conversation_id=st.session_state.selected_conversation)
        else:
            logger.info("No conversation available")

    condition_load_callback = bool(len(rev_conversation_list))
    load_conversation_button = st.button(
        "Load Conversation",
        key="load_conversation_button",
        use_container_width=True,
        on_click=lambda: update_load_boolean_callback(condition_load_callback),
    )
    ## Main

st.title(f"💬 Chatbot")
st.subheader(st.session_state.ongoing_conversation_id)

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.")
    st.stop()

chat = OpenAIChatbotBuilder(session_id=st.session_state.ongoing_conversation_id)
chat.build(
    openai_api_key=openai_api_key,
    model_name=st.session_state.openai_model,
    agent_tools=st.session_state.agent_tools,
)
agent_or_chain = chat()

container = st.container()
container.empty()
rewrite_conversation(chat.message_history.messages)

if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(parent_container=container)
    response = agent_or_chain.run(prompt, callbacks=[st_callback])
    st.write(response)

# with container_top:
#     with col2:
#         st.session_state
