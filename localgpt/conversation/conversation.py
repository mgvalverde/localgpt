import streamlit as st
from typing import Type, List
from langchain.schema import BaseMessage
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.memory import ConversationBufferMemory
from ..memory.tinydb import TinyDBChatMessageHistory
from ..utils import generate_uuid


class OpenAIChatbotBuilder:
    session_id = None
    llm = None
    tool_names: List = []
    tools: List = []
    message_history = None
    conversation_memory = None

    def __init__(self, session_id: str = None):
        if session_id is not None:
            self.session_id = session_id
        else:
            self.new_conversation()

    def new_conversation(self):
        self.session_id = generate_uuid()

    def build(
        self,
        openai_api_key,
        model_name="gpt-3.5-turbo",
        agent_tools=["llm-math"],
    ):
        self.llm = ChatOpenAI(
            temperature=0,
            streaming=True,
            model_name=model_name,
            openai_api_key=openai_api_key,
        )
        self.message_history = TinyDBChatMessageHistory(session_id=self.session_id)
        self.conversation_memory = ConversationBufferMemory(
            memory_key="history", chat_memory=self.message_history, return_messages=True
        )
        self.tool_names = agent_tools

    def __call__(self):
        if self.tool_names:
            self.tools = load_tools(self.tool_names, llm=self.llm)
            return initialize_agent(
                tools=self.tools,
                llm=self.llm,
                memory=self.conversation_memory,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
            )
        else:
            return ConversationChain(
                llm=self.llm,
                memory=self.conversation_memory,
                verbose=True,
            )


def rewrite_conversation(messages: List[Type[BaseMessage]], *args, **kwargs):
    mapping = {"human": "user", "ai": "assistant"}
    for message in messages:
        _type = mapping.get(message.type, "unk")
        st.chat_message(_type).write(message.content)


class ConversationManager:
    def __int__(self, memory, *args, **kwargs):
        self.memory = memory
        self.db = memory.db

    def new_conversation(self):
        st.session_state.conversation_id = generate_uuid()

    def build(self, conversation_id: str):
        ...

    def list_conversations(self):
        ...

    def get_conversation(self, conversation_id: str):
        ...

    def rewrite_conversation(self, messages):
        ...
        ## memory.messages

    def run(self, agent_or_chain):
        ...
