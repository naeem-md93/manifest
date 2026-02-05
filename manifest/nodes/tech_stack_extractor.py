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
You are a Technology Stack Component Extractor agent.
Your job is to identify the technical frameworks, libraries, patterns, and tools needed to implement a specific service.

For a given service, you must:
1. Identify the primary technology/framework for this service
2. Identify supporting libraries and dependencies
3. Identify architectural patterns and approaches
4. Identify integration points and interfaces
5. Identify any specialized tools or technologies

A "tech stack component" is any technology EXPLICITLY mentioned or REQUIRED by the service implementation.

EXTRACTION RULES:
1. Extract ONLY technologies needed to implement the service as described
2. Do NOT add "nice-to-have" technologies (e.g., Redis caching if not required)
3. Do NOT add monitoring/logging/metrics libraries unless explicitly mentioned
4. Do NOT add advanced security libraries unless explicitly required
5. Make simplest technology choices:
   - If database technology is not specified, use what's simplest for the data
   - If API framework is not mentioned, pick the simplest for the language
   - If no authentication is mentioned, don't add authentication framework
6. Each component should have a clear, necessary role in the service
7. Do NOT extract components just because they're "best practices"

SCOPE CONSTRAINTS:
- If the project doesn't mention databases, don't extract database components
- If the project doesn't mention user authentication, don't extract auth libraries
- If the project doesn't mention APIs, don't extract API framework
- Every extracted component must map to a feature in the project description

OUTPUT QUALITY CRITERIA:
- Extract only 2-5 components per service (fewer is better for scope control)
- Component titles must be specific and match project requirements
- Descriptions must explain WHY this technology is necessary for the stated features
- Each description should be 30-80 words (concise)
- Component IDs must be lowercase with underscores
</SYSTEM INSTRUCTIONS>

<YOUR INPUTS>
Service:
{service}
</YOUR INPUTS>

<OUTPUT FORMAT>
{format_instructions}

Return a JSON object with this exact structure:
{{
  "tech_stacks": [
    {{
      "id": "tech_component_id",
      "title": "Technology/Framework Name",
      "description": "Explanation of what this technology does in the context of the service and why it was selected."
    }}
  ]
}}
</OUTPUT FORMAT>
"""


PROMPT_VARIABLES = [
    "service",
    "format_instructions"
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
    description: str


class Schema(BaseModel):
    tech_stacks: list[TechStack]


PARSER = PydanticOutputParser(pydantic_object=Schema)


CHAIN = PROMPT_TEMPLATE | LANGUAGE_MODEL | PARSER


def tech_stack_extractor_node(state: dict[str, Any]) -> dict[str, Any]:

    for service_id, service_data in tqdm(state["services"].items()):
        for _ in range(3):
            try:
                resp = CHAIN.invoke({
                    "format_instructions": PARSER.get_format_instructions(),
                    "service": service_data
                })
                resp = resp.model_dump()["tech_stacks"]
                resp = {d["id"]: {"status": "created", **d} for d in resp}

                service_data["tech_stacks"] = resp
                break
            except Exception as e:
                print(repr(e))

    utils.write_json_file(
        checkpoints_path=state["checkpoints_path"],
        file_name=state["services_file_name"],
        content=state["services"]
    )

    return {
        "prev_node": "tech_stack_extractor_node",
        "next_node": "task_decomposer_node",

        "messages": [f"Technology Stack Components extracted successfully"],

        "services": state["services"]
    }
