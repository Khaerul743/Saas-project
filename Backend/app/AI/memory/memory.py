import logging
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

try:
    from mem0 import Memory
except ImportError:
    raise ImportError(
        "mem0 library is not installed. Please install it with: pip install mem0ai"
    )

load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)


# Simple Custom Exception
class MemoryError(Exception):
    """Base exception for memory operations"""

    pass


class MemoryControl:
    def __init__(
        self,
        memory_provider: str,
        provider_host: str,
        provider_port: str,
    ) -> None:
        """
        Initialize MemoryControl with simple error handling.

        Args:
            memory_provider: The memory provider (e.g., 'qdrant', 'pinecone')
            provider_host: Host address of the memory provider
            provider_port: Port number of the memory provider
        """
        try:
            # Basic validation
            if not all([memory_provider, provider_host, provider_port]):
                raise MemoryError(
                    "Semua parameter (memory_provider, provider_host, provider_port) harus diisi!"
                )

            # Create configuration
            self.config = {
                "vector_store": {
                    "provider": memory_provider,
                    "config": {"host": provider_host, "port": provider_port},
                }
            }

            # Initialize memory
            self.memory = Memory.from_config(self.config)
            print(f"Memory berhasil di setup dengan provider: {memory_provider}")

        except Exception as e:
            print(f"Error saat setup memory: {str(e)}")
            raise MemoryError(f"Gagal setup memory: {str(e)}") from e

    def get_context(self, query: str, memory_id: str, limit: int = 3) -> str:
        """
        Retrieve context from memory based on query.

        Args:
            query: Search query string
            memory_id: User ID for memory retrieval
            limit: Maximum number of results to return (default: 3)
        """
        try:
            # Basic validation
            if not query or not memory_id:
                raise MemoryError("Query dan memory_id tidak boleh kosong!")

            # Search memory
            get_memory = self.memory.search(query=query, user_id=memory_id, limit=limit)

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
            print(f"Error saat mengambil context: {str(e)}")
            raise MemoryError(f"Gagal mengambil context: {str(e)}") from e

    def add_context(self, list_messages: List, memory_id: str) -> Dict[str, Any]:
        """
        Add context to memory.

        Args:
            list_messages: List of messages to add to memory
            memory_id: User ID for memory storage
        """
        try:
            # Basic validation
            if not list_messages or not memory_id:
                raise MemoryError("list_messages dan memory_id tidak boleh kosong!")

            # Add to memory
            result = self.memory.add(list_messages, user_id=memory_id)
            return result

        except Exception as e:
            print(f"Error saat menambah context: {str(e)}")
            raise MemoryError(f"Gagal menambah context: {str(e)}") from e

    def delete_memory(
        self, memory_id: str, memory_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Delete memories from storage.

        Args:
            memory_id: User ID for memory deletion
            memory_ids: Optional list of specific memory IDs to delete
        """
        try:
            if not memory_id:
                raise MemoryError("memory_id tidak boleh kosong!")

            # Delete memories
            if memory_ids:
                result = self.memory.delete(memory_ids=memory_ids, user_id=memory_id)
            else:
                result = self.memory.delete(user_id=memory_id)

            return result

        except Exception as e:
            print(f"Error saat menghapus memory: {str(e)}")
            raise MemoryError(f"Gagal menghapus memory: {str(e)}") from e

    def get_all_memories(self, memory_id: str):
        """
        Get all memories for a user.

        Args:
            memory_id: User ID for memory retrieval
        """
        try:
            if not memory_id:
                raise MemoryError("memory_id tidak boleh kosong!")

            memories = self.memory.get_all(user_id=memory_id)
            return memories

        except Exception as e:
            print(f"Error saat mengambil semua memory: {str(e)}")
            raise MemoryError(f"Gagal mengambil semua memory: {str(e)}") from e


if __name__ == "__main__":
    try:
        # Example usage with simple error handling
        memory = MemoryControl("qdrant", "localhost", "6333")

        # Test get_context
        context = memory.get_context("Siapakah nama saya?", "default")
        print(f"Context: {context}")

        # Test add_context
        messages = [
            {"role": "user", "content": "Halo, nama saya John"},
            {
                "role": "assistant",
                "content": "Halo John! Senang berkenalan dengan Anda.",
            },
        ]
        result = memory.add_context(messages, "default")
        print(f"Add result: {result}")

    except MemoryError as e:
        print(f"Memory Error: {e}")
    except Exception as e:
        print(f"Error tidak terduga: {e}")
