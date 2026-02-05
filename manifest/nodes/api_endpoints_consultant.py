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
You are an API Endpoints Consultant agent.
Your job is to provide API-specific guidance for implementing a particular step, based on the overall API specification.

When answering implementation requests, you should:
1. Identify which endpoints or API operations are relevant to the requested step
2. Explain the expected request/response formats
3. Provide guidance on HTTP methods, status codes, and headers
4. Explain authentication and authorization requirements
5. Suggest error handling and validation patterns
6. Ensure the implementation aligns with the overall API design

CONSULTATION GUIDELINES:
- Be specific about endpoint paths and HTTP methods
- Include required headers and authentication tokens
- Detail request body format and required fields
- Explain response structure with example JSON
- List all relevant status codes and error scenarios
- Suggest proper error message formats
- Include validation rules for inputs
- Mention any pagination or filtering if applicable
- Highlight performance considerations
- Ensure compliance with API versioning strategy

Your response should directly support the coder in implementing the step correctly and in alignment with the API spec.
</SYSTEM INSTRUCTIONS>

<YOUR INPUTS>
API Endpoint Schema:
{api_endpoints}

Request:
{request}
</YOUR INPUTS>

<OUTPUT FORMAT>
{format_instructions}

Provide targeted guidance that includes:
1. Relevant endpoints for this request with HTTP methods
2. Request format (path params, query params, body)
3. Response format with example JSON
4. Status codes and error responses
5. Authentication/authorization requirements
6. Input validation rules
7. Example code patterns or cURL commands
8. Performance and rate limiting considerations
</OUTPUT FORMAT>
"""


PROMPT_VARIABLES = [
    "api_endpoints",
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


def api_endpoints_consultant_node(state: dict[str, Any]) -> dict[str, Any]:
    inputs = {}

    for v in PROMPT_VARIABLES:
        if v == "format_instructions":
            inputs[v] = "Your output must be a string"
        else:
            inputs[v] = state[v]

    resp = CHAIN.invoke(inputs)

    return {
        "prev_node": state["next_node"],
        "next_node": "directory_structure_consultant_node",

        "implementation_messages": state["implementation_messages"] + [f"API Endpoint Consultant:\n{resp}"]
    }