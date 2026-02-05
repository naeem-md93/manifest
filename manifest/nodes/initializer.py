import json
from typing import Any
import os
import shutil

from manifest import utils


def create_venv_if_not_exists(project_dir: str) -> str:

    if os.path.exists(os.path.join(project_dir, '.venv')):
        return "virtual environment already exists"

    _ = utils.execute_command(
        ["python3.12", "-m", "venv", ".venv"],
        cwd=project_dir
    )

    return "Virtual environment created"


def init_git(project_dir: str, branch: str = "main") -> str:

    if os.path.exists(os.path.join(project_dir, ".git")):
        return "git already exists"

    utils.execute_command(
        command=["git", "init", "-b", branch],
        cwd=project_dir,
    )

    shutil.copy(
        os.path.join(f'./manifest/data/gitignores/Python.gitignore'),
        f"{project_dir}/.gitignore",
    )

    utils.execute_command(
        command=["git", "add", "-A"],
        cwd=project_dir,
    )

    utils.execute_command(
        command=["git", "commit", "-m", "initialized git & added .gitignore"],
        cwd=project_dir,
    )

    return "initialized git & added .gitignore"


def initializer_node(state: dict[str, Any]) -> dict[str, Any]:

    checkpoints_path = os.path.join(state["project_dir"], ".manifest_cache")

    os.makedirs(state["project_dir"], exist_ok=True)
    os.makedirs(checkpoints_path, exist_ok=True)

    venv_msg = create_venv_if_not_exists(state["project_dir"])
    git_msg = init_git(state["project_dir"])



    return {
        "prev_node": "initializer_node",
        "next_node": "implementor_node",

        "checkpoints_path": checkpoints_path,

        "messages": open(os.path.join(checkpoints_path, "messages.md"), "r").read().splitlines(),
        "messages_file_name": "messages.md",

        "tech_doc": open(os.path.join(checkpoints_path, "tech_doc.md"), "r").read(),
        "tech_doc_file_name": "tech_doc.md",

        "services": json.load(open(os.path.join(checkpoints_path, "steps.json"))),
        "services_file_name": "services.json",

        "database_schema": open(os.path.join(checkpoints_path, "database_schema.md")).read(),

        "directory_structure": open(os.path.join(checkpoints_path, "directory_structure.md")).read(),

        "api_endpoints": open(os.path.join(checkpoints_path, "api_endpoints.md")).read(),

        "implementation_messages_file_name": "implementation_messages.md",
    }



    return {
        "prev_node": "initializer_node",
        "next_node": "document_writer_node",

        "checkpoints_path": checkpoints_path,

        "messages": [venv_msg, git_msg, "Project initialized successfully"],
        "messages_file_name": "messages.md",

        "tech_doc_file_name": "tech_doc.md",

        "services_file_name": "services.json",

        "implementation_messages_file_name": "implementation_messages.md",
    }
