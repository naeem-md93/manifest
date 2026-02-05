import json
import subprocess
import logging
import os
from typing import Any


def execute_command(command: list[str], cwd: str, **kwargs) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=kwargs.get('capture_output', True),
        text=kwargs.get('text', True),
        check=kwargs.get('check', True),
    )
    return result.stdout


def get_logger(name):
    # Configure the logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create a logger (can be associated with a specific module or class)
    logger = logging.getLogger(name) # Use __name__ for the current module
    return logger


def remove_fences(text: str) -> str:
    if text.startswith("```"):
        first_word = text.split("\n")[0]
        first_word = first_word.split(" ")[0]
        text = text[len(first_word):]

    if text.endswith("```"):
        text = text[:-len("```")]

    return text


def write_reports(checkpoints_path: str, file_name: str, messages: list[str]) -> None:
    os.makedirs(checkpoints_path, exist_ok=True)
    text = "\n----------\n".join(messages)
    with open(os.path.join(checkpoints_path, file_name), "w") as f:
        f.write(text)


def write_document(checkpoints_path: str, file_name: str, content: str):
    os.makedirs(checkpoints_path, exist_ok=True)
    content = remove_fences(content)
    with open(os.path.join(checkpoints_path, file_name), "w") as f:
        f.write(content)


def write_json_file(checkpoints_path: str, file_name: str, content: dict[Any, Any] | list[Any]):
    os.makedirs(checkpoints_path, exist_ok=True)
    with open(os.path.join(checkpoints_path, file_name), "w") as f:
        json.dump(content, f, indent=4, ensure_ascii=False)