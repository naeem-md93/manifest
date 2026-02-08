from typing import Any
import copy


def step_selector_node(state: dict[str, Any]) -> dict[str, Any]:

    selected = False
    sv_id = state["selected_service_id"]
    ts_id = state["selected_tech_stack_id"]
    ta_id = state["selected_task_id"]
    steps = state["services"][sv_id]["tech_stacks"][ts_id]["tasks"][ta_id]["steps"]
    for i in range(len(steps)):
        _id = list(steps.keys())[i]
        step = steps[_id]
        if step["status"] != "finished":
            current_idx = i
            current_id = _id
            current_step = step
            selected = True
            break

    if not selected:
        return {
            "prev_node": state["next_node"],
            "next_node": "task_selector_node",
            "messages": [f"All steps of the current task are implemented successfully"],
        }

    return {
        "prev_node": state["next_node"],
        "next_node": "implementor_node",

        "messages": [f"Step {current_idx} selected successfully"],

        "selected_step_index": current_idx,
        "selected_step_id": current_id,
    }