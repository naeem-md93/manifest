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
You are a Service Extractor agent specializing in architectural decomposition.
Your job is to parse a technical design document and extract individual, independent services.

A "service" is a logical, self-contained component that:
- Handles a specific domain or responsibility
- Can be developed and deployed independently
- Has clear interfaces and dependencies
- Represents a meaningful architectural boundary

Examples of services:
- User Authentication Service
- Note Management Service
- Payment Processing Service
- Notification Service

EXTRACTION RULES:
1. Extract ONLY services that are explicitly or clearly required by the project description
2. Do NOT invent services not mentioned (e.g., don't add admin service if not required)
3. Do NOT add cross-cutting services like logging, monitoring, or analytics unless explicitly mentioned
4. Make minimal assumptions - if a service is questionable, it probably isn't needed
5. Assign each service a descriptive ID (e.g., "auth_service", "note_manager")
6. Titles should be clear and match the project description terminology
7. Descriptions should explain ONLY the responsibility mentioned in the project
8. Maximum services: only extract what's needed for the stated requirements
9. Each service must be distinct and non-overlapping

SCOPE CONSTRAINTS:
- Do NOT extract services for features not explicitly mentioned in the project
- If the project doesn't mention authentication, don't extract auth service
- If the project doesn't mention notifications, don't extract notification service
- Stick strictly to the stated requirements

OUTPUT QUALITY CRITERIA:
- Each service description must be 40-100 words (concise, not elaborated)
- Service IDs must be lowercase with underscores, no spaces
- Service titles must be concise (2-4 words)
- All services must be directly required by the project description
</SYSTEM INSTRUCTIONS>

<YOUR INPUTS>
Technical Document:
{tech_doc}
</YOUR INPUTS>

<OUTPUT FORMAT>
{format_instructions}

Return a JSON object with this exact structure:
{{
  "services": [
    {{
      "id": "service_id_snake_case",
      "title": "Clear Service Title",
      "description": "Detailed explanation of what this service does, its responsibilities, and key features."
    }}
  ]
}}
</OUTPUT FORMAT>
"""


PROMPT_VARIABLES = [
    "tech_doc",
    "format_instructions",
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
    description: str


class Schema(BaseModel):
    services: list[Service]


PARSER = PydanticOutputParser(pydantic_object=Schema)


CHAIN = PROMPT_TEMPLATE | LANGUAGE_MODEL | PARSER


def service_extractor_node(state: dict[str, Any]) -> dict[str, Any]:

    for _ in range(3):
        try:
            resp = CHAIN.invoke({
                "format_instructions": PARSER.get_format_instructions(),
                "tech_doc": state["tech_doc"],
            })

            resp = resp.model_dump()["services"]
            resp = {d["id"]: {"status": "created", **d} for d in resp}
            break
        except Exception as e:
            print(repr(e))

    utils.write_json_file(
        checkpoints_path=state["checkpoints_path"],
        file_name=state["services_file_name"],
        content=resp
    )

    return {
        "prev_node": "service_extractor_node",
        "next_node": "tech_stack_extractor_node",

        "messages": [f"{len(resp)} Services extracted successfully"],

        "services": resp
    }
