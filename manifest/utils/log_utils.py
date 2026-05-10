from typing import Any
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
    AnyMessage
)


DELIMITER = "  \n# ===================================  \n"


def reformat_user_message(message: HumanMessage) -> str:

    text: str = ""
    text += "## `Human` Message:  \n"
    text += f"#### Content:  \n"
    text += f"{message.content}  \n"

    return text



def reformat_assistant_message(message: AIMessage) -> str:
    name: str = getattr(message, "name", "Unknown")
    content: str = getattr(message, "content", "")
    tool_calls: list[dict[str, Any]] = getattr(message, "tool_calls", [])

    text: str = f"## `{name}` Assistant Message:  \n"
    text += f"#### Content:  \n"
    text += f"{content}  \n"

    if tool_calls:
        text += f"#### Tool Calls:  \n"
        for tc in tool_calls:
            text += f"* #### \t Name: `{tc['name']}`  \n"
            text += f"* #### \t Args:  \n"
            for arg_name, arg_value in tc['args'].items():
                text += f"- **`{arg_name}`:**  {str(arg_value)}  \n"

    return text


def reformat_tool_message(message: ToolMessage) -> str:
    name: str = getattr(message, "name", "Unknown")
    content: str = getattr(message, "content", "")

    text: str = f"## `{name}` Tool Message:  \n"
    text += f"#### Content:  \n"
    text += f"{content}  \n"

    return text


def reformat_system_message(message: SystemMessage) -> str:

    name: str = getattr(message, "name", "Unknown")
    content: str = getattr(message, "content", "")

    text: str = f"## `{name}` System Message:  \n"
    text += f"#### Content:  \n"
    text += f"{content}  \n"

    return text



def reformat_message(message: AnyMessage) -> str:
    if isinstance(message, HumanMessage):
        return reformat_user_message(message) + DELIMITER
    elif isinstance(message, AIMessage):
        return reformat_assistant_message(message) + DELIMITER
    elif isinstance(message, ToolMessage):
        return reformat_tool_message(message) + DELIMITER
    elif isinstance(message, SystemMessage):
        return reformat_system_message(message) + DELIMITER
    else:
        raise TypeError(f"Unsupported message type: {type(message)}")


def reformat_messages(messages: list[AnyMessage]) -> str:
    return "".join([reformat_message(msg) for msg in messages])
