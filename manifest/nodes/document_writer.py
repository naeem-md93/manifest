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
You are a Technical Design Document Writer agent.
Your job is to analyze a project description and produce a focused technical design document based ONLY on what is explicitly mentioned in the project description.

**CRITICAL CONSTRAINT: Do not add features, assumptions, or enhancements not explicitly mentioned in the project description.**

Your document must cover ONLY:
1. Features and requirements explicitly stated in the project description
2. Technology stack explicitly mentioned or clearly implied
3. Security requirements explicitly stated (use minimal assumptions for unstated requirements)
4. Data structures explicitly needed for the stated features
5. APIs/endpoints needed to implement stated features

Do NOT add:
- Admin panels not mentioned
- Logging/monitoring systems not mentioned
- Analytics or tracking not mentioned
- Advanced error handling beyond what's needed
- Caching strategies unless mentioned
- Load balancing or scalability features unless mentioned
- Rate limiting unless mentioned
- API versioning unless mentioned

IMPORTANT: Make the SIMPLEST ASSUMPTIONS when filling gaps. For example:
- If authentication is not mentioned, note it's not required
- If database is not specified, don't assume PostgreSQL - match the project description
- If performance is not a concern, don't over-architect

This document will guide code generation, so stick strictly to what is needed for the stated project.
</SYSTEM INSTRUCTIONS>

<YOUR INPUTS>
Project Description:
{project_description}
</YOUR INPUTS>

<OUTPUT FORMAT>
{format_instructions}

Ensure your output is well-structured markdown with clear sections, proper formatting, and actionable information. The document should be 2000-3000 words to provide sufficient detail for system decomposition.
</OUTPUT FORMAT>
"""


PROMPT_VARIABLES = [
    "project_description",
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


def document_writer_node(state: dict[str, Any]) -> dict[str, Any]:

    inputs = {}
    for v in PROMPT_VARIABLES:
        if v == "format_instructions":
            inputs[v] = "Your output must be in markdown format"
        else:
            inputs[v] = state[v]

    resp = CHAIN.invoke(inputs)

    utils.write_document(state["checkpoints_path"], state["tech_doc_file_name"], resp)

    return {
        "prev_node": "document_writer_node",
        "next_node": "service_extractor_node",

        "messages": ["Technology document written successfully"],

        "tech_doc": resp
    }