from langchain_core.messages import AIMessage, HumanMessage, BaseMessage

def get_history_messages(messages: list[BaseMessage]):
    history_messages = ""
    for message in messages:
        if isinstance(message, HumanMessage):
            history_messages += f"Human: {message.content}\n"
        elif isinstance(message, AIMessage):
            history_messages += f"AI: {message.content}\n"
    return history_messages
