from typing import Any
from langgraph.graph import END
from langgraph.types import Command

from manifest import utils


def router_node(state: dict[str, Any]) -> str:

    if state.get("messages", []):
        utils.write_reports(
            state["checkpoints_path"],
            state["messages_file_name"],
            state["messages"]
        )

    if state.get("implementation_messages", []):
        utils.write_reports(
            state["checkpoints_path"],
            state["implementation_messages_file_name"],
            state["implementation_messages"]
        )

    return state.get("next_node", END)

