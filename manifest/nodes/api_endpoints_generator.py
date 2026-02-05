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
You are an API Endpoint Generator agent.
Your job is to propose REST API endpoints based STRICTLY on the implementation plan and project requirements.

**CRITICAL: Only create endpoints that are explicitly needed by the project.**

ENDPOINT DESIGN RULES:
1. Create endpoints ONLY for operations explicitly mentioned in the project
2. Use simple, standard HTTP methods (GET, POST, PUT, DELETE)
3. Avoid adding "nice-to-have" endpoints
4. Do NOT add:
   - Admin endpoints unless mentioned
   - Bulk operations unless mentioned
   - Filtering/sorting unless mentioned
   - Advanced query parameters unless mentioned
   - Pagination unless mentioned
   - Rate limiting unless mentioned

SCOPE CONSTRAINTS:
- Only create CRUD endpoints for entities that exist
- If search isn't mentioned, don't add search endpoints
- If filtering isn't mentioned, don't add it
- If pagination isn't mentioned, don't add it
- If export/reporting isn't mentioned, don't add it
- Every endpoint must map to a feature in the project description

ENDPOINT SPECIFICATION:
- Endpoint path
- HTTP method
- Required inputs (body/parameters)
- Response format
- Status codes (200, 201, 400, 404, 500 - only those applicable)
- Error response format

OUTPUT FORMAT:
Provide only the endpoints STRICTLY needed. Include:
1. Base URL and authentication method (only if needed)
2. Endpoint list with paths, methods, inputs, outputs
3. Data schemas for requests/responses
4. Example interactions

IMPORTANT: Minimal endpoints for maximal project functionality. Don't add extras.
</SYSTEM INSTRUCTIONS>

<YOUR INPUTS>
Implementation Plan:
{implementation_plan}
</YOUR INPUTS>

<OUTPUT FORMAT>
{format_instructions}

Create an API specification with ONLY endpoints explicitly required by the project.
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


def api_endpoints_generator_node(state: dict[str, Any]) -> dict[str, Any]:
    inputs = {}

    for v in PROMPT_VARIABLES:
        if v == "format_instructions":
            inputs[v] = "Your output must be a string"
        else:
            inputs[v] = state[v]

    resp = CHAIN.invoke(inputs)

    utils.write_document(
        state["checkpoints_path"],
        "api_endpoints.md",
        resp
    )

    return {
        "prev_node": state["next_node"],
        "next_node": "directory_structure_generator_node",

        "messages": [f"API Endpoint Schema generated successfully"],

        "api_endpoints": resp,

    }