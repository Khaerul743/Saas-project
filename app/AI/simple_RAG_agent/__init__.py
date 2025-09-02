from typing import Any, Dict

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.workflow import Workflow


class Agent:
    def __init__(
        self,
        directory_path: str,
        chromadb_path: str,
        collection_name: str,
        include_memory=False,
    ):
        self.workflow = Workflow(
            directory_path=directory_path,
            chromadb_path=chromadb_path,
            collection_name=collection_name,
            include_memory=include_memory,
        )
        self._history_messages = None

    def execute(self, state: Dict, thread_id):
        result = self.workflow.run(state=state, thread_id=thread_id)
        self._history_messages = result["messages"]
        return result

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
    while True:
        user_input = input("Human: ")
        if user_input == "exit":
            print("bye bye")
            break
        agent.execute(
            {"user_message": user_input},
            "thread_123",
        )
