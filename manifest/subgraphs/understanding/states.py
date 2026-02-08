from typing import TypedDict
from typing import Annotated
import operator


class UnderstandingInputState(TypedDict):
    project_dir: str
    project_desc: str
    checkpoints_path: str


class UnderstandingState(TypedDict):
    project_dir: str
    project_desc: str
    checkpoints_path: str

    messages: Annotated[list[str], operator.add]

    draft: str

    functional_domains: str
    technical_layers: str
    database_schema: str
    api_endpoints: str
    directory_structure: str

    document: str


