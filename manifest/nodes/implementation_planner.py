from typing import Any


def implementation_planner_node(state: dict[str, Any]) -> dict[str, Any]:

    implementation_plan = ""
    for service_id, service_data in state["services"].items():
        implementation_plan += f"Service: {service_data['title']}\n"

        for tech_stack_id, tech_stack_data in service_data["tech_stacks"].items():
            implementation_plan += f"\t- Tech Stack: {tech_stack_data['title']}\n"

            for task_id, task_data in tech_stack_data["tasks"].items():
                implementation_plan += f"\t\t- Task: {task_data['title']}\n"

                for step_id, step_data in task_data["steps"].items():
                    implementation_plan += f"\t\t\t- Step: {step_data['title']}\n"

    return {
        "prev_node": state["next_node"],
        "next_node": "database_schema_generator_node",

        "messages": [f"Implementation plan generated successfully."],

        "implementation_plan": implementation_plan,
    }