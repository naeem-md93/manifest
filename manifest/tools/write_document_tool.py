import os
from pathlib import Path
from langchain.tools import tool, ToolRuntime

from manifest.schemas import ManifestState
from manifest.utils import py_utils, log_utils

@tool(parse_docstring=True)
def write_document_tool(agent_name: str, document: str, runtime: ToolRuntime[ManifestState]) -> str:
    """Tool to write and store a document

    Args:
        agent_name (str): Name of the agent writing the document.
        document (str): Document content to write.

    Returns:
        str: Status of operation
    """

    if not runtime.context.documents.get(agent_name):
        runtime.context.documents[agent_name] = []
    runtime.context.documents[agent_name].append(document)

    path: Path = runtime.context.cache_dir / f"{agent_name}.md"
    py_utils.append_text_file(path, document + log_utils.DELIMITER)

    return f"Document written successfully!"
