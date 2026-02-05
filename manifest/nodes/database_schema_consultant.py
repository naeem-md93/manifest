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
You are a Database Schema Consultant agent.
Your job is to provide database-specific guidance for implementing a particular step, based on the overall database schema.

When answering implementation requests, you should:
1. Identify which tables are involved in the requested step
2. Explain the relevant columns, relationships, and constraints
3. Provide guidance on data validation and constraints
4. Suggest appropriate queries or operations
5. Highlight any database-specific considerations (indexes, transactions, etc.)
6. Ensure the implementation aligns with the overall schema design

CONSULTATION GUIDELINES:
- Be specific about table names, column names, and data types
- Reference foreign key relationships if relevant
- Mention any cascading deletes or updates
- Suggest indexes if performance is relevant to the request
- Include error handling for constraint violations
- Provide examples of expected SQL or ORM patterns
- Highlight any transactions needed for data consistency
- Consider edge cases and data validation

Your response should directly support the coder in implementing the step correctly and safely.
</SYSTEM INSTRUCTIONS>

<YOUR INPUTS>
Database Schema:
{database_schema}

Request:
{request}
</YOUR INPUTS>

<OUTPUT FORMAT>
{format_instructions}

Provide targeted guidance that includes:
1. Relevant tables and fields for this request
2. Specific data types and constraints to respect
3. Relationship details if joining multiple tables
4. Validation rules and business constraints
5. Example queries or code patterns
6. Edge cases and error handling considerations
7. Performance considerations if applicable
</OUTPUT FORMAT>
"""


PROMPT_VARIABLES = [
    "database_schema",
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


def database_schema_consultant_node(state: dict[str, Any]) -> dict[str, Any]:

    inputs = {}

    for v in PROMPT_VARIABLES:
        if v == "format_instructions":
            inputs[v] = "Your output must be a string"
        else:
            inputs[v] = state[v]

    resp = CHAIN.invoke(inputs)

    return {
        "prev_node": state["next_node"],
        "next_node": "api_endpoints_consultant_node",

        "implementation_messages": state["implementation_messages"] + [f"Database Consultant:\n{resp}"]
    }
