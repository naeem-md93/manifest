from typing import Any
import copy


def task_selector_node(state: dict[str, Any]) -> dict[str, Any]:

    selected = False
    sv_id = state["selected_service_id"]
    ts_id = state["selected_tech_stack_id"]
    tasks = state["services"][sv_id]["tech_stacks"][ts_id]["tasks"]
    for i in range(len(tasks)):
        _id = list(tasks.keys())[i]
        task = tasks[_id]
        if not all(v["status"] == "finished" for v in task["steps"].values()):
            current_idx = i
            current_id = _id
            current_task = task
            selected = True
            break

    if not selected:
        return {
            "prev_node": state["next_node"],
            "next_node": "tech_stack_selector_node",
            "messages": [f"All tasks of the current tech stack are implemented successfully"],
        }
    return {
        "prev_node": state["next_node"],
        "next_node": "step_selector_node",

        "messages": [f"Task {current_idx} selected successfully"],

        "selected_task_index": current_idx,
        "selected_task_id": current_id,
    }

