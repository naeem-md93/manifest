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
You are a Step Decomposer agent specializing in atomic-level implementation planning.
Your job is to split each task into atomic steps - the smallest meaningful units of implementation work.

A "step" represents the MINIMUM work needed to complete one discrete piece of functionality - nothing more, nothing less.

DECOMPOSITION RULES:
1. Break each task into 2-4 steps ONLY (focus on essentials)
2. Do NOT add steps for error handling beyond what's explicitly needed
3. Do NOT add validation steps unless the project requires validation
4. Do NOT add logging or debugging steps unless mentioned
5. Do NOT add code cleanup or refactoring steps
6. Steps should follow logical execution order
7. Each step should touch ONE primary file or concern
8. Assign sequential, descriptive IDs (e.g., "models_user_create")

SCOPE CONSTRAINTS:
- Every step must implement something explicitly mentioned in the project
- If input validation isn't mentioned, don't require validation steps
- If error handling isn't mentioned, implement only critical error cases
- If the project doesn't require it, don't add it

OUTPUT QUALITY CRITERIA:
- Step titles must be specific and minimal (e.g., "Create User model", not "Create, test, and validate User model")
- Descriptions must be 40-80 words and state:
  * EXACTLY what file(s) will be created/modified
  * EXACT functions/classes to implement (only what's needed)
  * Expected code length (should be minimal)
  * HOW success will be verified
- Each step should be completable with minimal code (~30-50 lines max)
- Step IDs must be lowercase with underscores
- Include only necessary patterns (skip optional enhancements)
- Each step must be essential to the project
</SYSTEM INSTRUCTIONS>

<YOUR INPUTS>
Task:
{task}
</YOUR INPUTS>

<OUTPUT FORMAT>
{format_instructions}

Return a JSON object with this exact structure:
{{
  "steps": [
    {{
      "id": "step_id_snake_case",
      "title": "Specific, Implementation-Focused Title",
      "description": "Detailed, actionable description including files, specific classes/functions, complexity estimate, and verification method."
    }}
  ]
}}
</OUTPUT FORMAT>
"""


PROMPT_VARIABLES = [
    "task",
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


class Step(BaseModel):
    id: str
    title: str
    description: str


class Schema(BaseModel):
    steps: list[Step]


PARSER = PydanticOutputParser(pydantic_object=Schema)


CHAIN = PROMPT_TEMPLATE | LANGUAGE_MODEL | PARSER


def step_decomposer_node(state: dict[str, Any]) -> dict[str, Any]:

    for service_id, service_data in tqdm(state["services"].items()):
        for tech_stack_id, tech_stack_data in service_data["tech_stacks"].items():
            for task_id, task_data in tech_stack_data["tasks"].items():
                for _ in range(3):
                    try:
                        resp = CHAIN.invoke({
                            "format_instructions": PARSER.get_format_instructions(),
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
