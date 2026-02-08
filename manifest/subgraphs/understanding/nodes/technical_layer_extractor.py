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
You are a Technical Layer Extractor agent in a Project Development System.
Given a project document, your job is to extract essential technical layers in this project\
 (e.g. front end, back-end, database, AI/ML, etc).
These technical layers **MUST** be either **explicitly mentioned by the user** or **vital for the project**.
If you want to make assumptions about a technical layers, you must make the simplest ones.

<OUTPUT FORMAT>
Your output must be in markdown (.md) format.
</OUTPUT FORMAT>
</SYSTEM INSTRUCTIONS>
<INPUTS>
Project Draft:
{draft}
</INPUTS>
"""


PROMPT_VARIABLES = [
    "draft"
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


def technical_layer_extractor_node(state: dict[str, Any]) -> dict[str, Any]:

    # resp = utils.read_text_file(os.path.join(state["checkpoints_path"], "technical_layers.md"))

    resp = CHAIN.invoke({
        "draft": state["draft"],
    })
    utils.write_document(state["checkpoints_path"], "technical_layers.md", resp)

    return {
        "messages": ["Technical layers were extracted successfully"],
        "technical_layers": resp
    }