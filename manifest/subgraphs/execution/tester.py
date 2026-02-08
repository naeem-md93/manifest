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
You are a Tester agent responsible for writing minimal tests for implemented code.
Your job is to create test code that verifies the implementation works for its specified purpose.

**CRITICAL: Write ONLY tests for the functionality specified. Do NOT add extra tests or edge cases not mentioned.**

TESTING PRINCIPLES (MINIMAL):
1. Test ONLY the core functionality specified
2. Test the happy path (normal usage)
3. Test ONLY critical error cases
4. Do NOT test edge cases unless mentioned
5. Do NOT test performance unless mentioned
6. Do NOT test security unless mentioned
7. Do NOT add extra test utilities or fixtures
8. Do NOT add complex test setup unless needed

TEST COVERAGE (FOCUSED):
- Test that the code does what it's supposed to do
- Test critical error cases only
- Test data integrity if database operations
- Test API endpoints with basic inputs
- Avoid unnecessary test complexity

WHAT TO INCLUDE:
- Tests for the main functionality
- Tests for critical error cases only
- Basic test setup if needed

WHAT TO EXCLUDE:
- Edge case tests unless mentioned
- Performance tests
- Security tests
- Load tests
- Extensive fixtures/setup
- Complex mocking unless critical
- Tests for features not in the request

OUTPUT REQUIREMENTS:
- Output ONLY test code, no explanations
- Include only necessary imports and setup
- Include only necessary test functions
- Tests should be simple and readable
- Code should be ready to run immediately
</SYSTEM INSTRUCTIONS>

<YOUR INPUTS>
Implementation Request:
{request}

Implementation Messages:
{implementation_messages}
</YOUR INPUTS>

<OUTPUT FORMAT>
{format_instructions}

Your output MUST be minimal, focused test code. Write ONLY tests for the specified functionality. No explanations, no extras.
</OUTPUT FORMAT>
"""


PROMPT_VARIABLES = [
    "request",
    "implementation_messages",
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


PARSER = StrOutputParser()


CHAIN = PROMPT_TEMPLATE | LANGUAGE_MODEL | PARSER


def tester_node(state: dict[str, Any]) -> dict[str, Any]:

    inputs = {}

    for v in PROMPT_VARIABLES:
        if v == "format_instructions":
            inputs[v] = "Your output MUST be codes. You must not explain or add extra texts"
        else:
            inputs[v] = state[v]

    resp = CHAIN.invoke(inputs)

    return {
        "prev_node": state["next_node"],
        "next_node": "validator_node",

        "implementation_messages": state["implementation_messages"] + [f"Tester Agent:\n{resp}"],
    }
