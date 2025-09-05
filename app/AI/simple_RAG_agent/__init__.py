import os
from typing import Any, Dict

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.AI.simple_RAG_agent.workflow import Workflow


class Agent:
    def __init__(
        self,
        directory_path: str,
        chromadb_path: str,
        collection_name: str,
        model_llm: str,
        include_memory=False,
    ):
        self.directory_path = directory_path
        self.workflow = Workflow(
            directory_path=directory_path,
            chromadb_path=chromadb_path,
            collection_name=collection_name,
            include_memory=include_memory,
            model_llm=model_llm,
        )
        self._history_messages = None

    def execute(self, state: Dict, thread_id):
        result = self.workflow.run(state=state, thread_id=thread_id)
        self._history_messages = result["messages"]
        return result

    def add_document(
        self, file_name: str, file_type: str, document_id: str, db, document, file_path
    ):
        if not os.path.exists(self.directory_path + "/"):
            os.makedirs(self.directory_path, exist_ok=True)
        documents = self.workflow.rag.load_single_document(
            self.directory_path, file_name, file_type, db, document, file_path
        )
        self.workflow.rag.add_documents(documents, document_id)

    def delete_document(self, document_id: str):
        try:
            self.workflow.rag.delete_document(document_id)
        except Exception as e:
            raise

    def pretty_print(self):
        if self._history_messages is None:
            print("No messages found.")
            return
        messages = ""
        print(self._history_messages)
        for message in self._history_messages:
            if isinstance(message, HumanMessage):
                msg = f"=========Human=========\n{message.content}\n\n"
            elif isinstance(message, AIMessage):
                if message.content == "":
                    msg = f"=========ToolCall=========\nTool Name: {message.tool_calls[0]['name']}\nparams: {message.tool_calls[0]['args']}\n\n"
                msg = f"=========AI=========\n{message.content}\n\n"
            elif isinstance(message, ToolMessage):
                msg = f"=========Tool Message=========\n{message.content}\n\n"
            else:
                continue
            messages += msg

        print(messages)
        return


if __name__ == "__main__":
    agent = Agent("docs", "data", "my_collections")
    # agent.add_document("peler.pdf", "pdf")
    while True:
        user_input = input("Human: ")
        if user_input == "exit":
            print("bye bye")
            break
        agent.execute(
            {"user_message": user_input},
            "thread_123",
        )
#
