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
You are a Validator agent responsible for checking if an implementation step is correct and complete.
Your job is to verify that the implementation EXACTLY matches what was requested - no more, no less.

**CRITICAL: Check for scope compliance. Flag if extra features/code were added that weren't requested.**

VALIDATION CRITERIA:
1. SCOPE COMPLIANCE
   - Does the code implement ONLY what was requested?
   - Are there extra features not in the request?
   - Are there extra error handling not mentioned?
   - Are there extra validation not mentioned?
   - Flag ANY additions beyond the request

2. FUNCTIONAL CORRECTNESS
   - Does the code do what it's supposed to do?
   - Are the tests passing?
   - Does it handle the basic cases?

3. INTEGRATION
   - Does it follow the database schema?
   - Does it match the API specification?
   - Does it follow the directory structure?

4. CODE QUALITY (MINIMAL)
   - Is the code readable?
   - Does it follow basic conventions?
   - Is it simple and focused?

VALIDATION RULES:
- If tests fail, send back for fixing
- If code is overly complex, send back for simplification
- If extra features were added, send back for removal
- If scope is exceeded, send back for correction
- If core functionality is missing, send back for implementation

OUTPUT GUIDANCE:
- finished (true/false): Only true if code is correct AND doesn't exceed scope
- request (string): If not finished, provide specific feedback:
  * What is missing or incorrect
  * What extra code should be removed (if scope exceeded)
  * Which tests failed
  * Any integration problems
  * What specifically needs to be fixed

Example feedback formats:
- "Tests failed for user creation endpoint. Need to fix the validation error handling."
- "Implementation includes logging which wasn't requested. Remove the logging code before accepting."
- "Database transaction handling isn't implemented as specified in schema. Need to add proper constraints."
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

class Schema(BaseModel):
    finished: bool = Field(..., description="Whether the request is implemented correctly.")
    request: str = Field(..., description="the updated request")


PARSER = PydanticOutputParser(pydantic_object=Schema)


CHAIN = PROMPT_TEMPLATE | LANGUAGE_MODEL | PARSER


def validator_node(state: dict[str, Any]) -> dict[str, Any]:

    inputs = {}

    for v in PROMPT_VARIABLES:
        if v == "format_instructions":
            inputs[v] = PARSER.get_format_instructions()
        else:
            inputs[v] = state[v]

    resp = CHAIN.invoke(inputs)

    resp = resp.model_dump()

    if resp["finished"]:
        return {
            "prev_node": state["next_node"],
            "next_node": "status_updater_node",
        }

    return {
        "prev_node": state["next_node"],
        "next_node": "database_schema_consultant_node",

        "request": resp["request"],
    }