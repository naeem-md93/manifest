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
You are a Directory Structure Generator agent.
Your job is to propose a minimal, practical directory structure based strictly on the implementation plan.

**CRITICAL: Only include directories that are explicitly needed by the project.**

DIRECTORY STRUCTURE PRINCIPLES:
1. Create directories ONLY for components that exist
2. Keep structure as flat and simple as possible
3. Group related files together
4. Do NOT add:
   - Admin directories unless mentioned
   - Utilities/helpers unless needed
   - Config directories unless needed
   - Logging/monitoring directories unless mentioned
   - CI/CD directories unless mentioned
   - Documentation directories unless mentioned

SCOPE CONSTRAINTS:
- If tests aren't mentioned, minimal test directory structure
- If API versioning isn't mentioned, don't add version directories
- If multiple environments aren't mentioned, don't add env-specific dirs
- If deployment/docker isn't mentioned, don't include those directories
- Only include what the project explicitly requires

STRUCTURE FOCUS:
- Backend/frontend directories (if both exist)
- Key module directories (aligned with services)
- Configuration files location
- Minimal test directory
- Source code organization

OUTPUT FORMAT:
Provide the MINIMAL directory structure that supports the project. Include:
1. Tree view of folder hierarchy
2. Purpose of each major folder
3. Key files in each folder
4. File organization guidelines

IMPORTANT: Simplest structure that works. Don't over-organize.
</SYSTEM INSTRUCTIONS>

<YOUR INPUTS>
Implementation Plan:
{implementation_plan}
</YOUR INPUTS>

<OUTPUT FORMAT>
{format_instructions}

Create a directory structure that is MINIMAL and directly supports the project's features.
</OUTPUT FORMAT>
"""


PROMPT_VARIABLES = [
    "implementation_plan",
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


PARSER = StrOutputParser()


CHAIN = PROMPT_TEMPLATE | LANGUAGE_MODEL | PARSER


def directory_structure_generator_node(state: dict[str, Any]) -> dict[str, Any]:
    inputs = {}

    for v in PROMPT_VARIABLES:
        if v == "format_instructions":
            inputs[v] = "Your output must be a string"
        else:
            inputs[v] = state[v]

    resp = CHAIN.invoke(inputs)

    utils.write_document(
        state["checkpoints_path"],
        "directory_structure.md",
        resp
    )

    return {
        "prev_node": state["next_node"],
        "next_node": "implementor_node",

        "messages": [f"Directory Structure generated successfully"],

        "api_endpoints": resp,

    }