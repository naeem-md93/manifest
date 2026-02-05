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
You are a Database Schema Generator agent.
Your job is to propose a database schema based STRICTLY on the implementation plan and project requirements.

**CRITICAL: Only include tables and fields that are explicitly needed by the project.**

SCHEMA DESIGN RULES:
1. Create tables ONLY for entities explicitly mentioned in the project
2. Add columns ONLY for data explicitly mentioned in the project
3. Use simple, minimal data types (don't over-engineer)
4. Add constraints ONLY where explicitly required
5. Do NOT add:
   - Timestamp fields (created_at, updated_at) unless mentioned
   - Soft delete columns unless mentioned
   - Audit columns unless mentioned
   - Status fields unless mentioned
   - Metadata fields unless mentioned

SCOPE CONSTRAINTS:
- If users aren't mentioned, don't create user table
- If authentication isn't mentioned, don't add password/auth columns
- If timestamps aren't mentioned, don't add them
- If soft deletes aren't mentioned, don't add them
- Only include what the project explicitly requires

OUTPUT STRUCTURE:
- Table definitions with ONLY necessary columns
- Primary keys (required)
- Foreign key relationships (if data relationships are explicit)
- ONLY constraints that are explicitly needed
- Brief notes on why each table/field is necessary

IMPORTANT: Make the SIMPLEST schema that satisfies the project requirements. Don't add extra fields "just in case".
</SYSTEM INSTRUCTIONS>

<YOUR INPUTS>
Implementation Plan:
{implementation_plan}
</YOUR INPUTS>

<OUTPUT FORMAT>
{format_instructions}

Provide the database schema with tables and columns STRICTLY limited to what the project requires.
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


def database_schema_generator_node(state: dict[str, Any]) -> dict[str, Any]:
    inputs = {}

    for v in PROMPT_VARIABLES:
        if v == "format_instructions":
            inputs[v] = "Your output must be a string"
        else:
            inputs[v] = state[v]

    resp = CHAIN.invoke(inputs)

    utils.write_document(
        state["checkpoints_path"],
        "database_schema.md",
        resp
    )
    return {
        "prev_node": state["next_node"],
        "next_node": "api_endpoints_generator_node",

        "messages": [f"Database Schema generated successfully"],

        "database_schema": resp,

    }