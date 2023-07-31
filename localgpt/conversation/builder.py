import streamlit as st
from typing import Type, List
from langchain.schema import BaseMessage
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.memory import ConversationBufferMemory
from langchain.cache import InMemoryCache
from pathlib import Path
from ..memory.sqlite import SQLEnhancedChatMessageHistory
from ..utils import generate_uuid


class ChatbotAssistantBuilder:
    llm = None
    history = None
    memory = None
    tool_names: List = []


    def build_model(self, cls, *args, **kwargs):
        self.llm = cls(*args, **kwargs)

    def build_memory(self, cls, *args, **kwargs):
        self.history = cls(*args, **kwargs)
        self.memory = ConversationBufferMemory(
            memory_key="history",
            chat_memory=self.history,
            return_messages=True)

    def add_tool(self, tool_name: str):
        self.tool_names.append(tool_name)

    def add_tools(self, tool_name_list: List[str]):
        self.tool_names.extend(tool_name_list)

    def add_cache(self, cls, *args, **kwargs):
        cache = cls(*args, **kwargs)
        try:
            self.llm.cache = cache
        except AttributeError:
            raise AttributeError("Create a model before adding a cache")

    def __call__(self, *args, **kwargs):
        if self.tool_names:
            tools = load_tools(self.tool_names, llm=self.llm)
            return initialize_agent(
                tools=tools,
                llm=self.llm,
                memory=self.memory,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=kwargs.pop("verbose", True)
            )
        else:
            return ConversationChain(
                llm=self.llm,
                memory=self.memory,
                verbose=kwargs.pop("verbose", True)
            )


def get_chat_assistant(session_id,
                       connection_string,
                       api_key,
                       model,
                       tools,
                       **kwargs):
    table_name = kwargs.pop("table_name", "message_store")
    temperature = kwargs.pop("temperature", 0)
    streaming = kwargs.pop("streaming", True)

    builder = ChatbotAssistantBuilder()
    builder.build_memory(SQLEnhancedChatMessageHistory,
                         session_id=session_id,
                         connection_string=connection_string,
                         table_name=table_name)
    builder.build_model(ChatOpenAI,
                        temperature=temperature,
                        streaming=streaming,
                        model_name=model,
                        openai_api_key=api_key)
    builder.add_cache(InMemoryCache)
    builder.add_tools(tools)

    return builder()


def rewrite_conversation(messages: List[Type[BaseMessage]], container=None, upwards=False, *args, **kwargs):
    mapping = {"human": "user", "ai": "assistant"}

    if upwards:
        messages = reversed(messages)

    for message in messages:
        _type = mapping.get(message.type, "unk")
        if container is not None:
            st.chat_message(_type).write(message.content)
        else:
            container.chat_message(_type).write(message.content)
