from typing import Any
import copy


def tech_stack_selector_node(state: dict[str, Any]) -> dict[str, Any]:

    selected = False
    sv_id = state["selected_service_id"]
    tech_stacks = state["services"][sv_id]['tech_stacks']
    for i in range(len(tech_stacks)):
        _id = list(tech_stacks.keys())[i]
        tech_stack = tech_stacks[_id]
        if not all(v["status"] == "finished" for v in tech_stack["tasks"].values()):
            current_idx = i
            current_id = _id
            current_tech_stack = tech_stack
            selected = True
            break

    if not selected:
        return {
            "prev_node": state["next_node"],
            "next_node": "service_selector_node",
            "messages": ["All Tech stacks of the current service are selected."],
        }
    return {
        "prev_node": state["next_node"],
        "next_node": "task_selector_node",

        "messages": [f"Tech Stack {current_idx} selected successfully"],

        "selected_tech_stack_index": current_idx,
        "selected_tech_stack_id": current_id,
    }