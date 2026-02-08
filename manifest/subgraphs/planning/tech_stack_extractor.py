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
> You are a technical analyst.
> Given a **Technical Design Document (TDD)**, identify and extract **all technology stack components** required to implement the project.
>
> A technology stack component is a major implementation layer such as frontend, backend, database, infrastructure, AI/ML, integrations, messaging, or similar.
> Rules:
> * Focus **only** on components and their **explicit services** (e.g., authentication, authorization, notifications, background processing, caching).
> * Do **not** invent components or services not clearly implied by the TDD.
> * Do **not** include implementation tasks, steps, code, or testing details.
> * Use precise technical language and clear service boundaries.

</SYSTEM INSTRUCTIONS>

<YOUR INPUTS>
{tech_doc}
</YOUR INPUTS>

<OUTPUT FORMAT>
For **each** identified component, respond using **exactly** the following format:
{{
  "components": [
    {{
      "id": comp-xx (for example, comp-01, comp-02, ...)
      "title": <short, descriptive title>
      "summary": ~100 words summarizing the services EXPLICITLY involved in this component>
      "explanation": ~500 words explaining each service in detail, including responsibilities, interactions, and boundaries>
    }},
    ...
  ]
}}
</OUTPUT FORMAT>
"""


PROMPT_VARIABLES = [
    "tech_doc",
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



class TechStack(BaseModel):
    id: str
    title: str
    summary: str
    explanation: str


class Schema(BaseModel):
    components: list[TechStack]


PARSER = PydanticOutputParser(pydantic_object=Schema)


CHAIN = PROMPT_TEMPLATE | LANGUAGE_MODEL | PARSER


def tech_stack_extractor_node(state: dict[str, Any]) -> dict[str, Any]:

    resp = utils.read_json_file(os.path.join(state["checkpoints_path"], state["services_file_name"]))
    state["services"] = resp
    # for _ in range(3):
    #     try:
    #         resp = CHAIN.invoke({
    #             "tech_doc": state["tech_doc"],
    #         })
    #         resp = resp.model_dump()["components"]
    #         resp = {d["id"]: {"status": "created", **d} for d in resp}
    #         break
    #     except Exception as e:
    #         print(repr(e))
    #
    # utils.write_json_file(
    #     checkpoints_path=state["checkpoints_path"],
    #     file_name=state["services_file_name"],
    #     content=resp
    # )

    return {
        "prev_node": "tech_stack_extractor_node",
        "next_node": "service_extractor_node",

        "messages": [f"Technology Stack Components extracted successfully"],

        "services": state["services"]
    }
