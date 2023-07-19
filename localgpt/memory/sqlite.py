import json
from langchain.schema import BaseMessage, _message_to_dict
from langchain.memory import SQLChatMessageHistory
from sqlalchemy import Column, Integer, Text, TIMESTAMP
from sqlalchemy.sql import func
from datetime import datetime

try:
    from sqlalchemy.orm import declarative_base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base

_DEFAULT_TITLE = "Untitled Conversation"

def create_message_model(table_name, DynamicBase):  # type: ignore
    """
    Create a message model for a given table name.
    Args:
        table_name: The name of the table to use.
        DynamicBase: The base class to use for the model.

    Returns:
        The model class.

    """

    # Model declared inside a function to have a dynamic table name
    class Message(DynamicBase):
        __tablename__ = table_name
        id = Column(Integer, primary_key=True)
        session_id = Column(Text)
        message = Column(Text)
        _meta_created_at = Column(TIMESTAMP,
                                   default=datetime.utcnow)
        _meta_modified_at = Column(TIMESTAMP,
                                   default=datetime.utcnow,
                                   onupdate=datetime.utcnow)

    return Message

def create_mapping_model(table_name, DynamicBase):  # type: ignore
    """
    Create a message model for a given table name.
    Args:
        table_name: The name of the table to use.
        DynamicBase: The base class to use for the model.

    Returns:
        The model class.

    """

    # Model declared inside a function to have a dynamic table name
    class ConversationMetadata(DynamicBase):
        __tablename__ = table_name
        session_id = Column(Text, primary_key=True)
        title = Column(Text, default=_DEFAULT_TITLE)

    return ConversationMetadata

class SQLEnhancedChatMessageHistory(SQLChatMessageHistory):

    def _create_table_if_not_exists(self) -> None:
        DynamicBase = declarative_base()
        self.Message = create_message_model(self.table_name, DynamicBase)
        self.ConversationMetadata = create_mapping_model(self.table_meta_name, DynamicBase)
        # Create all does the check for us in case the table exists.
        DynamicBase.metadata.create_all(self.engine)

    @property
    def table_meta_name(self) -> str:
        return self.table_name + "_meta"

    def clear(self) -> None:
        """Clear session memory from db"""

        with self.Session() as session:
            session.query(self.Message).filter(
                self.Message.session_id == self.session_id
            ).delete()
            session.query(self.ConversationMetadata).filter(
                self.ConversationMetadata.session_id == self.session_id
            ).delete()
            session.commit()

    def list_chats(self, n=None):
        with self.Session() as session:
            TableA = self.Message
            TableB = self.ConversationMetadata

            subquery = session.query(TableA.session_id, func.max(TableA._meta_modified_at).label('_meta_modified_at')) \
                .group_by(TableA.session_id).subquery()
            query = session.query(subquery.c.session_id, TableB.title) \
                .join(TableB, TableB.session_id == subquery.c.session_id) \
                .order_by(subquery.c._meta_modified_at.desc())

            if n is not None:
                query = query.limit(n)

            result = query.all()
            mapping = {idx: title for idx, title in result}
            return mapping

    def upsert_title(self, title: str) -> None:
        """Update session title"""

        with self.Session() as session:
            session.query(self.ConversationMetadata).filter(
                self.ConversationMetadata.session_id == self.session_id
            ).delete()
            session.add(self.ConversationMetadata(session_id=self.session_id, title=title))
            session.commit()

    def add_message(self, message: BaseMessage) -> None:
        """Append the message to the record in db"""
        with self.Session() as session:
            jsonstr = json.dumps(_message_to_dict(message))
            session.add(self.Message(session_id=self.session_id, message=jsonstr))
            #TODO: refactor to extract the upsert title logic to a function

            is_in_metadata = session.query(self.ConversationMetadata).filter(
                self.ConversationMetadata.session_id == self.session_id
            ).count() > 0

            if not is_in_metadata:
                session.add(self.ConversationMetadata(session_id=self.session_id))
            session.commit()

    def delete(self) -> None:
        """Delete the message from the record in db"""
        with self.Session() as session:
            session.query(self.Message).filter(
                self.Message.session_id == self.session_id
            ).delete()
            session.commit()