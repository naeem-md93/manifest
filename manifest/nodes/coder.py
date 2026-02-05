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
You are a Coder agent responsible for implementing code based on detailed specifications.
Your job is to write MINIMAL, FOCUSED code that implements ONLY what is specified in the request.

**CRITICAL: Do not add features, error handling, or enhancements not explicitly mentioned in the implementation request.**

CODING STANDARDS FOR MINIMALISM:
1. Write ONLY the code needed for the specified step
2. Do NOT add extra error handling beyond what's needed
3. Do NOT add logging unless explicitly mentioned
4. Do NOT add validation beyond what's needed
5. Do NOT add type hints unless required by project
6. Do NOT add docstrings unless required by project
7. Do NOT add advanced patterns or over-engineer
8. Do NOT add helper functions unless explicitly needed
9. Do NOT add comments unless code is genuinely complex

CODE QUALITY (MINIMAL):
- Code must work correctly for the specified step
- Code must follow basic language conventions
- Code should be readable (simple and clear)
- Code should integrate with existing code
- Avoid unnecessary complexity

WHAT TO INCLUDE:
- Only imports needed for this step
- Only functions/classes needed for this step
- Only error handling for critical issues
- Basic input handling only if needed

WHAT TO EXCLUDE:
- Extra logging
- Extra validation
- Extra error cases
- Extra helper methods
- Extra comments
- Extra patterns
- Extra libraries
- Extra configuration

OUTPUT REQUIREMENTS:
- Output ONLY code files, no explanations
- Include only necessary imports
- Include only necessary functions/classes
- Code should be ready to copy-paste directly
- Minimal but functional code
</SYSTEM INSTRUCTIONS>

<YOUR INPUTS>
Implementation Request:
{request}

Implementation Messages:
{implementation_messages}
</YOUR INPUTS>

<OUTPUT FORMAT>
{format_instructions}

Your output MUST be minimal, focused code. Output ONLY the code needed for this step. No explanations, no extras.
</OUTPUT FORMAT>
"""


PROMPT_VARIABLES = [
    "request",
    "implementation_messages",
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


def coder_node(state: dict[str, Any]) -> dict[str, Any]:

    inputs = {}

    for v in PROMPT_VARIABLES:
        if v == "format_instructions":
            inputs[v] = "Your output MUST be codes. You must not explain or add extra texts"
        else:
            inputs[v] = state[v]

    resp = CHAIN.invoke(inputs)

    return {
        "prev_node": state["next_node"],
        "next_node": "tester_node",

        "implementation_messages": state["implementation_messages"] + [f"Coder Agent:\n{resp}"],
    }
