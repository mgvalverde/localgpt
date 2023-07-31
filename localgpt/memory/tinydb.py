import json
import logging
from typing import List
from langchain.schema import BaseChatMessageHistory
from langchain.schema.messages import BaseMessage, _message_to_dict, messages_from_dict
from ..utils import resolve_path

logger = logging.getLogger(__name__)


class TinyDBChatMessageHistory(BaseChatMessageHistory):
    """Chat message history that stores history in TinyDB.

    Args:
        connection_string: connection string to connect to MongoDB
        session_id: arbitrary key that is used to store the messages
            of a single chat session.
        database_name: name of the database to use
        collection_name: name of the collection to use
    """

    def __init__(
        self,
        session_id: str = "default",
        database_file: str = "~/.localgpt/chat_history_table.json",
    ):
        try:
            import tinydb
        except ImportError:
            raise ImportError(
                "Could not import tinydb  python package. "
                "Please install it with `pip install tinydb`."
            )

        from tinydb import TinyDB

        self.database_file: str = resolve_path(database_file)
        self.db: TinyDB = TinyDB(self.database_file)
        self.session_id: str = session_id

    @property
    def session_id(self):
        return self._session_id

    @session_id.setter
    def session_id(self, value):
        from tinydb.table import Table

        self._session_id = value
        self.table: Table = self.db.table(self.session_id)

    @property
    def messages(self) -> List[BaseMessage]:  # type: ignore
        """Retrieve the messages from TinyDB"""
        items = self.table.all()
        items_parsed = [json.loads(item["History"]) for item in items]
        return messages_from_dict(items_parsed)

    def add_message(self, message: BaseMessage) -> None:
        """Append the message to the record in TinyDB"""

        try:
            self.table.insert(
                {
                    "History": json.dumps(_message_to_dict(message)),
                }
            )
        except Exception as err:  # TODO: remove overly broad Exception clause
            logger.error(err)

    def clear(self) -> None:
        """Clear session memory from TinyDB"""

        try:
            self.db.drop_table(self.session_id)
        except Exception as err:  # TODO: remove overly broad Exception clause
            logger.error(err)
