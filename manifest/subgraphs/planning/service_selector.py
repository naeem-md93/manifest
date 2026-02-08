from typing import Any
import copy

from langgraph.graph import END


def service_selector_node(state: dict[str, Any]) -> dict[str, Any]:

    selected = False
    for i in range(len(state["services"])):
        _id = list(state["services"].keys())[i]
        service = state["services"][_id]
        if not all(v["status"] == "finished" for v in service["tech_stacks"].values()):
            current_idx = i
            current_id = _id
            current_service = service
            selected = True
            break

    if not selected:
        return {
            "prev_node": state["next_node"],
            "next_node": END,
            "messages": [f"All services finished."],
        }

    return {
        "prev_node": state["next_node"],
        "next_node": "tech_stack_selector_node",

        "messages": [f"Service {current_idx} selected successfully"],

        "selected_service_index": current_idx,
        "selected_service_id": current_id,
    }
