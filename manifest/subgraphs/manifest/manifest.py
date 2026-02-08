from typing import Any
from typing import TypedDict
from typing import Annotated
import operator


class ManifestInputState(TypedDict):
    project_dir: str
    project_description: str


class ManifestState(TypedDict):
    prev_node: str
    next_node: str

    project_dir: str
    project_description: str
    checkpoints_path: str

    messages: Annotated[list[str], operator.add]
    messages_file_name: str

    tech_doc: str
    tech_doc_file_name: str

    services: dict[str, dict[str, Any]]
    services_file_name: str

    implementation_plan: str

    database_schema: str

    directory_structure: str

    api_endpoints: str

    selected_service_index: int
    selected_service_id: str

    selected_tech_stack_index: int
    selected_tech_stack_id: str

    selected_task_index: int
    selected_task_id: str

    selected_step_index: int
    selected_step_id: str

    implementation_messages: list[str]
    implementation_messages_file_name: str

    request: str
