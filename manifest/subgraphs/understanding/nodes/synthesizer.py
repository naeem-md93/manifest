from typing import Any
import os
from pydantic import Field
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers import PydanticOutputParser

from manifest import utils


PROMPT = """<SYSTEM INSTRUCTIONS>
You are a Synthesizer agent in a Project Development System.
Given the following 5 aspects of a project, your job is to write a detailed implementation plan. These aspects are:
- Functional Domains
- Technical Layers
- Database Schema
- API Endpoints
- Directory Structure

If you want to make assumptions, you must make the simplest ones.

<OUTPUT FORMAT>
Your output must be in markdown (.md) format.
</OUTPUT FORMAT>
</SYSTEM INSTRUCTIONS>
<INPUTS>
Functional Domains:
{functional_domains}

Technical Layers:
{technical_layers}

Database Schema:
{database_schema}

API Endpoints:
{api_endpoints}

Directory Structure:
{directory_structure}
</INPUTS>
"""


PROMPT_VARIABLES = [
    "functional_domains",
    "technical_layers",
    "database_schema",
    "api_endpoints",
    "directory_structure",
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


def synthesizer_node(state: dict[str, Any]) -> dict[str, Any]:
    # resp = utils.read_text_file(os.path.join(state["checkpoints_path"], "document.md"))

    resp = CHAIN.invoke({
        "functional_domains": state["functional_domains"],
        "technical_layers": state["technical_layers"],
        "database_schema": state["database_schema"],
        "api_endpoints": state["api_endpoints"],
        "directory_structure": state["directory_structure"],

    })
    utils.write_document(state["checkpoints_path"], "document.md", resp)

    return {
        "messages": ["Synthesized document were generated successfully"],
        "document": resp
    }