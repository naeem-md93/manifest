from typing import Any
import os
from tqdm import tqdm
from pydantic import BaseModel
from pydantic import Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers import PydanticOutputParser
from manifest import utils


PROMPT = """
<SYSTEM INSTRUCTIONS>
> You are a low-level implementation planner.
> Given:
> * a **technology stack component description**,
> * a **service description within that component**, and
> * a **single implementation task**,
>   split the task into **multiple atomic implementation steps**.
>
> A step must:
> * Be **indivisible** (no further decomposition needed)
> * Result in a **single logical file change** (create, modify, or delete one file)
> * Be implemented **entirely within the explicit scope** of the given component, service, and task

> Rules:
> * Each step must correspond to **exactly one file change**.
> * Do **not** bundle multiple responsibilities into one step.
> * Do **not** include testing, validation, or deployment steps.
> * Do **not** reference other components or services.
> * Do **not** include code snippets or pseudocode.
> * Use precise, deterministic, and implementation-oriented language suitable for a coding agent.
</SYSTEM INSTRUCTIONS>

<YOUR INPUTS>
Technology Stack Component:
{component}

Service:
{service}

Task:
{task}
</YOUR INPUTS>

<OUTPUT FORMAT>
> Respond **only** in the following JSON format:
>
> ```json
> {{
>   "steps": [
>     {{
>       "id": "step-xx",  # for example, step-01, step-02, ...
>       "title": "Short, action-oriented step title",
>       "summary": "~100 words describing the concrete implementation instructions for this step",
>       "explanation": "~500 words explaining in detail how this step is implemented EXPLICITLY for this task and service within this component, including assumptions and constraints"
>     }},
>     ...
>   ]
> }}
> ```
</OUTPUT FORMAT>
"""


PROMPT_VARIABLES = [
    "component",
    "service",
    "task",
]


PROMPT_TEMPLATE = PromptTemplate(
    template=PROMPT,
    input_variables=PROMPT_VARIABLES
)


LANGUAGE_MODEL = ChatOpenAI(
    base_url=os.getenv("LMSTUDIO_LANGUAGE_BASE_URL"),
    api_key="<none>",
    model=os.getenv("LMSTUDIO_LANGUAGE_MODEL"),
    temperature=0.3
)


class Step(BaseModel):
    id: str
    title: str
    summary: str
    explanation: str


class Schema(BaseModel):
    steps: list[Step]


PARSER = PydanticOutputParser(pydantic_object=Schema)


CHAIN = PROMPT_TEMPLATE | LANGUAGE_MODEL | PARSER


def step_decomposer_node(state: dict[str, Any]) -> dict[str, Any]:

    resp = utils.read_json_file(os.path.join(state["checkpoints_path"], state["services_file_name"]))
    state["services"] = resp

    for component_id, component_data in tqdm(state["services"].items()):
        for service_id, service_data in component_data["services"].items():
            for task_id, task_data in service_data["tasks"].items():
                for _ in range(3):
                    try:
                        resp = CHAIN.invoke({
                            "component": {"id": component_id, "title": component_data["title"], "explanation": component_data["explanation"]},
                            "service": {"id": service_id, "title": service_data["title"], "explanation": service_data["explanation"]},
                            "task": task_data
                        })

                        resp = resp.model_dump()["steps"]
                        resp = {d["id"]: {"status": "created", **d} for d in resp}
                        task_data["steps"] = resp
                        break
                    except Exception as e:
                        print(repr(e))

    utils.write_json_file(
        state["checkpoints_path"],
        state["services_file_name"],
        state["services"]
    )

    return {
        "prev_node": state["next_node"],
        "next_node": "implementation_planner_node",

        "messages": [f"steps decomposed successfully."],

        "services": state["services"],
    }
