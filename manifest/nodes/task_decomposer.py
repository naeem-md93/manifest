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
You are a Task Decomposer agent specializing in breaking down technology stack components into implementable work units.
Your job is to decompose a technical stack component into specific, actionable tasks that can be worked on independently.

A "task" represents the MINIMUM work needed to implement a specific aspect of the technology component - nothing more.

DECOMPOSITION RULES:
1. Break down ONLY into tasks that directly implement the stated features
2. Do NOT create tasks for features not explicitly mentioned
3. Do NOT create tasks for refactoring, optimization, or cleanup
4. Do NOT create tasks for "nice-to-have" improvements
5. Do NOT add tasks for logging, monitoring, or analytics unless explicitly required
6. Tasks should follow logical dependency order
7. Each task should address ONE necessary aspect of the component
8. Assign unique, descriptive IDs (e.g., "setup_fastapi", "create_models")

SCOPE CONSTRAINTS:
- If authentication isn't mentioned, don't create auth tasks
- If caching isn't mentioned, don't create caching tasks
- If deployment isn't mentioned, don't create deployment tasks
- Every task must directly support a feature in the project description
- Avoid vague tasks - each task must map to specific functionality

OUTPUT QUALITY CRITERIA:
- Extract 2-5 tasks per tech component (fewer is better)
- Task titles must be action-oriented and specific ("Create User model", not "Database setup")
- Descriptions must be 50-100 words stating:
  * EXACTLY what feature this implements
  * WHAT needs to be done
  * KEY files/components involved
- Task IDs must be lowercase with underscores
- Avoid overlap between tasks
- No task should be "nice-to-have" or optional
</SYSTEM INSTRUCTIONS>

<YOUR INPUTS>
Technical Stack Component:
{tech_stack}
</YOUR INPUTS>

<OUTPUT FORMAT>
{format_instructions}

Return a JSON object with this exact structure:
{{
  "tasks": [
    {{
      "id": "task_id_snake_case",
      "title": "Action-Oriented Task Title",
      "description": "Detailed explanation of what needs to be implemented, why, and what deliverables are expected."
    }}
  ]
}}
</OUTPUT FORMAT>
"""


PROMPT_VARIABLES = [
    "tech_stack",
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

class Task(BaseModel):
    id: str
    title: str
    description: str


class Schema(BaseModel):
    tasks: list[Task]


PARSER = PydanticOutputParser(pydantic_object=Schema)


CHAIN = PROMPT_TEMPLATE | LANGUAGE_MODEL | PARSER


def task_decomposer_node(state: dict[str, Any]) -> dict[str, Any]:


    for service_id, service_data in tqdm(state["services"].items()):
        for tech_stack_id, tech_stack_data in service_data["tech_stacks"].items():
            for _ in range(3):
                try:
                    resp = CHAIN.invoke({
                        "format_instructions": PARSER.get_format_instructions(),
                        "tech_stack": tech_stack_data
                    })
                    resp = resp.model_dump()["tasks"]
                    resp = {d["id"]: {"status": "created", **d} for d in resp}

                    tech_stack_data["tasks"] = resp
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
        "next_node": "step_decomposer_node",

        "messages": [f"tasks decomposed successfully."],

        "services": state["services"]
    }