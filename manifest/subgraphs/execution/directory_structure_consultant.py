from typing import Any
import os
from pydantic import BaseModel
from pydantic import Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers import PydanticOutputParser


PROMPT = """
<SYSTEM INSTRUCTIONS>
You are a Directory Structure Consultant agent.
Your job is to provide file organization and placement guidance for implementing a particular step, based on the overall directory structure.

When answering implementation requests, you should:
1. Identify the correct directory/location for files needed by this step
2. Explain the proper naming conventions for the project
3. Provide guidance on file organization and module structure
4. Suggest related files or imports needed
5. Ensure the implementation follows the established project organization

CONSULTATION GUIDELINES:
- Be specific about which directory the file should go in
- Include the exact file path and name
- Explain any module structure or __init__.py requirements
- Suggest how imports should be organized
- Recommend file naming conventions being used
- Identify any configuration files that might be needed
- Mention any dependencies or related files
- Explain how this file fits into the overall structure
- Suggest testing file location if applicable
- Include any build or deployment script updates needed

Your response should directly support the coder in placing and organizing files correctly within the project.
</SYSTEM INSTRUCTIONS>

<YOUR INPUTS>
Directory Structure:
{directory_structure}

Request:
{request}
</YOUR INPUTS>

<OUTPUT FORMAT>
{format_instructions}

Provide targeted guidance that includes:
1. Exact file path and location for this step
2. File naming convention and format
3. Directory organization principles to follow
4. Module structure and __init__.py patterns
5. Import statements and dependencies
6. Related files to be aware of
7. Configuration or setup files needed
8. Testing file location and naming
9. Build/deployment script updates if applicable
</OUTPUT FORMAT>
"""


PROMPT_VARIABLES = [
    "directory_structure",
    "request",
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


def directory_structure_consultant_node(state: dict[str, Any]) -> dict[str, Any]:

    inputs = {}

    for v in PROMPT_VARIABLES:
        if v == "format_instructions":
            inputs[v] = "Your output must be a string"
        else:
            inputs[v] = state[v]

    resp = CHAIN.invoke(inputs)

    return {
        "prev_node": state["next_node"],
        "next_node": "coder_node",

        "implementation_messages": state["implementation_messages"] + [f"Directory Structure Consultant:\n{resp}"]
    }