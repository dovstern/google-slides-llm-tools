from langchain_core.messages import AIMessage, AnyMessage
from langchain_core.messages import RemoveMessage
from typing import List

def add_credentials_to_langchain_tool_call(credentials, state: dict, messages_key: str) -> List[AnyMessage]:
    """
    Add credentials to a LangChain tool call.
    """
    messages = state[messages_key]
    last_message = messages[-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            tool_call.args["credentials"] = credentials
    return {messages_key: [RemoveMessage(id=last_message.id), last_message]}