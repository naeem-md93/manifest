from typing import Any


def implementor_node(state: dict[str, Any]) -> dict[str, Any]:

    sv_id = state.get("selected_service_id")

    if (not sv_id) or (state["services"][sv_id]["status"] == "finished"):
        return {
            "prev_node": state["next_node"],
            "next_node": "service_selector_node",
            "messages": ["Service is not selected or is finished!"],
        }

    ts_id = state.get("selected_tech_stack_id")
    if (not ts_id) or (state["services"][sv_id]["tech_stacks"][ts_id]["status"] == "finished"):
        return {
            "prev_node": state["next_node"],
            "next_node": "tech_stack_selector_node",
            "messages": ["Tech Stack is not selected or is finished!"],
        }

    ta_id = state.get("selected_task_id")
    if (not ta_id) or (state["services"][sv_id]["tech_stacks"][ts_id]["tasks"][ta_id]["status"] == "finished"):
        return {
            "prev_node": state["next_node"],
            "next_node": "task_selector_node",
            "messages": ["Task is not selected or is finished!"],
        }

    st_id = state.get("selected_step_id")
    if (not st_id) or (state["services"][sv_id]["tech_stacks"][ts_id]["tasks"][ta_id]["steps"][st_id]["status"] == "finished"):
        return {
            "prev_node": state["next_node"],
            "next_node": "step_selector_node",
            "messages": ["Step is not selected or is finished!"],
        }

    request = state["services"][sv_id]["tech_stacks"][ts_id]["tasks"][ta_id]["steps"][st_id]["description"]

    return {
        "prev_node": state["next_node"],
        "next_node": "database_schema_consultant_node",

        "messages": ["Service, Tech Stack, Task, and Step selected successfully!"],
        "request": request,
        "implementation_messages": [f"Implementation Instruction:\n{request}"]
    }