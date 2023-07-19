from pathlib import Path
import streamlit as st
import re
import importlib
import uuid
from .memory.sqlite import SQLEnhancedChatMessageHistory

import logging

logger = logging.getLogger(__name__)


def generate_uuid():
    return uuid.uuid4().hex


def reset_conversation():
    st.session_state.update(ongoing_conversation_id=generate_uuid())


def update_load_boolean_callback(cond: bool, key, value):
    if cond:
        st.session_state.update(**{key: value})
    else:
        logger.info("No conversation available")


def check_import(module):
    try:
        importlib.import_module(module)
    except ImportError:
        raise ImportError(
            f"""Could not import the `tinydb` Python package. 
            "Please install it with `pip install {module}`."""
        )


def resolve_path(path: str, mkdir: bool = True) -> str:
    """Extract the path from the connection string"""
    path_res = Path(path).expanduser().resolve()
    if mkdir:
        path_res.parent.mkdir(parents=True, exist_ok=True)
    return str(path_res)


def get_meta_path(fpath: str) -> str:
    """Return the path to the metadata file"""
    return re.sub(r"(.[a-zA-Z0-9]{3,4}$)", r"_meta\1", fpath)


def preprocess_title(title, length: int = 5):
    _ = title.split()
    if len(_) > length:
        _ = _[:length]
        prep_title = " ".join(_) + "..."
    else:
        prep_title = " ".join(_)
    return prep_title.title()


def delete_conversation(conversation_id: str, connection_string: str, table_name: str):
    """Delete a conversation from the database"""
    return SQLEnhancedChatMessageHistory(
        session_id=conversation_id,
        connection_string=connection_string,
        table_name=table_name
    ).delete()
