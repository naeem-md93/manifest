from typing import Any
import os
from pydantic import BaseModel
from pydantic import Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers import PydanticOutputParser

from manifest import utils


PROMPT = """
<SYSTEM INSTRUCTIONS>
> You are a software architecture analyst.
> Given a **single technology stack component description** (including its summary and explanation), extract **all services explicitly involved in that component**.
>
> A service is a distinct functional capability such as authentication, authorization, user management, notifications, background jobs, caching, logging, monitoring, payments, search, or similar.
>
> Rules:
>
> * Extract **only services explicitly stated or clearly implied** by the component description.
> * Do **not** invent services that are not supported by the input.
> * Describe implementation **from the perspective of this component only** (no cross-component deep dives).
> * Do **not** include code, tasks, steps, APIs, or testing details.
> * Use precise, technical, and implementation-oriented language.

</SYSTEM INSTRUCTIONS>

<YOUR INPUTS>
Technology Stack Component:
{component}
</YOUR INPUTS>

<OUTPUT FORMAT>
> Respond **only** in the following JSON format:
>
> ```json
> {{
>   "services": [
>     {{
>       "id": "service-xx",  # (for example, service-01, service-02, ...)
>       "title": "Short service name",
>       "summary": "~100 words describing how this service is implemented EXPLICITLY within this component",
>       "explanation": "~500 words explaining in detail how this service is implemented EXPLICITLY in this component, including responsibilities, internal workflows, and interactions with other services"
>     }}
>   ]
> }}
> ```
</OUTPUT FORMAT>
"""


PROMPT_VARIABLES = [
    "component",
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


class Service(BaseModel):
    id: str
    title: str
    summary: str
    explanation: str


class Schema(BaseModel):
    services: list[Service]


PARSER = PydanticOutputParser(pydantic_object=Schema)


CHAIN = PROMPT_TEMPLATE | LANGUAGE_MODEL | PARSER


def service_extractor_node(state: dict[str, Any]) -> dict[str, Any]:


    resp = utils.read_json_file(os.path.join(state["checkpoints_path"], state["services_file_name"]))
    state["services"] = resp

    # for component_id, component_data in state["services"].items():
    #     for _ in range(3):
    #         try:
    #             resp = CHAIN.invoke({
    #                 "component": component_data,
    #             })
    #
    #             resp = resp.model_dump()["services"]
    #             resp = {d["id"]: {"status": "created", **d} for d in resp}
    #             component_data["services"] = resp
    #             break
    #         except Exception as e:
    #             print(repr(e))
    #
    # utils.write_json_file(
    #     checkpoints_path=state["checkpoints_path"],
    #     file_name=state["services_file_name"],
    #     content=state["services"]
    # )

    return {
        "prev_node": "service_extractor_node",
        "next_node": "task_decomposer_node",

        "messages": [f"{len(state['services'])} Services extracted successfully"],

        "services": state["services"]
    }
