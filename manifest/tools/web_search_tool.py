from langchain.tools import tool

from manifest.chains.web_search_chain import run_web_search_chain


@tool(parse_docstring=True)
def web_search_tool(query: str) -> str:
    """Tool to search on the Web.

    Args:
        query (str): The query to search on the internet.

    Returns:
        str: A response to the query from the internet.
    """

    resp = run_web_search_chain(query)

    return resp