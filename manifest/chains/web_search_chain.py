from langchain_core.output_parsers import StrOutputParser

from manifest.utils import llm_utils

SYSTEM_PROMPT = """
Your are a helpful assistant acting as a web search tool.
Given a search query, you must provide helpful response.
Your response must be 250 tokens at most.
"""

PARSER = StrOutputParser()


LLM = llm_utils.build_language_model(
    name="web_search_model",
    temperature=0.9,
    max_tokens=300,
)


def run_web_search_chain(query: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Search query:\n" + query},
    ]

    chain = LLM | PARSER

    resp: str = chain.invoke(messages)

    return resp
