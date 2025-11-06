from typing import Any, Dict, Sequence

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from mem0 import Memory


class LongTermMemory:
    def __init__(self, memory_id: str):
        self.memory_id = memory_id
        # Initialize memory
        self.memory = Memory.from_config(
            {
                "vector_store": {
                    "provider": "qdrant",
                    "config": {"host": "localhost", "port": "6333"},
                }
            }
        )

    def get_context(self, query: str, limit: int = 3) -> str:
        """
        Retrieve context from memory based on query.

        Args:
            query: Search query string
            memory_id: User ID for memory retrieval
            limit: Maximum number of results to return (default: 3)
        """
        try:
            # Search memory
            get_memory = self.memory.search(
                query=query, user_id=self.memory_id, limit=limit
            )

            # Format results
            if not get_memory.get("results"):
                return ""

            memories = "\n".join(
                [
                    f"- {entry.get('memory', '')}"
                    for entry in get_memory["results"]
                    if entry.get("memory")
                ]
            )
            return memories

        except Exception as e:
            raise e

    def add_context(self, list_messages: Sequence[BaseMessage]) -> Dict[str, Any]:
        """
        Add context to memory.

        Args:
            list_messages: List of messages to add to memory
            memory_id: User ID for memory storage
        """
        try:
            formatted_messages = self._message_saving_format(list_messages)
            # Add to memory
            result = self.memory.add(formatted_messages, user_id=self.memory_id)
            return result

        except Exception as e:
            raise e

    def delete_memory(self) -> Dict[str, Any]:
        """
        Delete memories from storage.

        Args:
            memory_id: User ID for memory deletion
            memory_ids: Optional list of specific memory IDs to delete
        """
        try:
            # Delete memories
            result = self.memory.delete(self.memory_id)

            return result

        except Exception as e:
            raise e

    def get_all_memories(self):
        """
        Get all memories for a user.

        Args:
            memory_id: User ID for memory retrieval
        """
        try:
            memories = self.memory.get_all(user_id=self.memory_id)
            return memories

        except Exception as e:
            raise e

    def _message_saving_format(self, messages):
        formatted = []
        for message in messages:
            data = {}
            if isinstance(message, HumanMessage):
                data["role"] = "user"
                data["content"] = message.content
                formatted.append(data)
            elif isinstance(message, AIMessage):
                data["role"] = "assistant"
                data["content"] = message.content
                formatted.append(data)
        return formatted
