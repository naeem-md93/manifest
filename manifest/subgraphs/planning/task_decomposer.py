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
> You are a senior implementation planner.
> Given:
> * a **technology stack component description**, and
> * a **single service description within that component**,
>   decompose the work required to implement that service into **multiple concrete implementation tasks**.
>
> A task represents a meaningful, independently implementable unit of work that contributes directly to delivering the service **within the explicit scope of the given component**.
> Rules:
> * Decompose the service into **multiple logical tasks**, not steps.
> * Each task must be **directly tied** to the given service and component.
> * Do **not** include work belonging to other components or services.
> * Do **not** include atomic steps, code, APIs, testing, or deployment details.
> * Do **not** invent functionality not supported by the input descriptions.
> * Use precise, implementation-focused technical language.

</SYSTEM INSTRUCTIONS>

<YOUR INPUTS>
Technology Stack Component:
{component}

Service:
{service}
</YOUR INPUTS>

<OUTPUT FORMAT>
> Respond **only** in the following JSON format:
>
> ```json
> {{
>   "tasks": [
>     {{
>       "id": "task-xx",  # task-01, task-02, ...
>       "title": "Short task name",
>       "summary": "~100 words describing how this task will be implemented",
>       "explanation": "~500 words explaining in detail how this task is implemented EXPLICITLY for this service within this component"
>     }}
>   ]
> }}
</OUTPUT FORMAT>
"""


PROMPT_VARIABLES = [
    "component"
    "service",
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

class Task(BaseModel):
    id: str
    title: str
    summary: str
    explanation: str


class Schema(BaseModel):
    tasks: list[Task]


PARSER = PydanticOutputParser(pydantic_object=Schema)


CHAIN = PROMPT_TEMPLATE | LANGUAGE_MODEL | PARSER


def task_decomposer_node(state: dict[str, Any]) -> dict[str, Any]:

    resp = utils.read_json_file(os.path.join(state["checkpoints_path"], state["services_file_name"]))
    state["services"] = resp
    # for component_id, component_data in tqdm(state["services"].items()):
    #     for service_id, service_data in component_data["services"].items():
    #         for _ in range(3):
    #             try:
    #                 resp = CHAIN.invoke({
    #                     "component": {
    #                         "id": component_id,
    #                         "title": component_data["title"],
    #                         "summary": component_data["summary"],
    #                         "explanation": component_data["explanation"]
    #                     },
    #                     "service": service_data
    #                 })
    #                 resp = resp.model_dump()["tasks"]
    #                 resp = {d["id"]: {"status": "created", **d} for d in resp}
    #
    #                 service_data["tasks"] = resp
    #                 break
    #             except Exception as e:
    #                 print(repr(e))
    #
    #
    # utils.write_json_file(
    #     state["checkpoints_path"],
    #     state["services_file_name"],
    #     state["services"]
    # )

    return {
        "prev_node": state["next_node"],
        "next_node": "step_decomposer_node",

        "messages": [f"tasks decomposed successfully."],

        "services": state["services"]
    }