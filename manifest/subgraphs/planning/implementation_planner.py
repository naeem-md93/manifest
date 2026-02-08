from typing import Any


def implementation_planner_node(state: dict[str, Any]) -> dict[str, Any]:

    implementation_plan = ""
    for component_id, component_data in state["services"].items():
        implementation_plan += f"Tech Stack Component: {component_data['summary']}\n"

        for service_id, service_data in component_data["services"].items():
            implementation_plan += f"\t- Service: {service_data['summary']}\n"

            for task_id, task_data in service_data["tasks"].items():
                implementation_plan += f"\t\t- Task: {task_data['summary']}\n"

                for step_id, step_data in task_data["steps"].items():
                    implementation_plan += f"\t\t\t- Step: {step_data['summary']}\n"

    return {
        "prev_node": state["next_node"],
        "next_node": "database_schema_generator_node",

        "messages": [f"Implementation plan generated successfully."],

        "implementation_plan": implementation_plan,
    }