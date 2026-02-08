from typing import Any


def status_updater_node(state: dict[str, Any]) -> dict[str, Any]:

    sv_id = state["selected_service_id"]
    ts_id = state["selected_tech_stack_id"]
    ta_id = state["selected_task_id"]
    st_id = state["selected_step_id"]

    state["services"][sv_id]["tech_stacks"][ts_id]["tasks"][ta_id]["steps"][st_id]["status"] = "finished"
    messages = [f"Step {st_id} implemented successfully!"]

    if all(v["status"] == "finished" for v in state["services"][sv_id]["tech_stacks"][ts_id]["tasks"][ta_id]["steps"].values()):
        state["services"][sv_id]["tech_stacks"][ts_id]["tasks"][ta_id]["status"] = "finished"
        messages.append(f"Task {ta_id} implemented successfully!")

    if all(v["status"] == "finished" for v in state["services"][sv_id]["tech_stacks"][ts_id]["tasks"].values()):
        state["services"][sv_id]["tech_stacks"][ts_id]["status"] = "finished"
        messages.append(f"Tech stack {ts_id} implemented successfully!")

    if all(v["status"] == "finished" for v in state["services"][sv_id]["tech_stacks"].values()):
        state["services"][sv_id]["status"] = "finished"
        messages.append(f"Service {sv_id} implemented successfully!")

    return {
        "prev_node": state["next_node"],
        "next_node": "implementor_node",

        "messages": messages,
        "implementation_messages": []
    }

