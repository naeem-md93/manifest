from typing import Any
import os
import json
import hashlib
import logging
import requests
import subprocess


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


def create_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def read_text_file(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def read_text_file_if_exists(path: str) -> str:
    if os.path.exists(path):
        return read_text_file(path)
    return ""


def write_text_file(checkpoints_path: str, file_name: str, data: str) -> None:

    os.makedirs(checkpoints_path, exist_ok=True)

    with open(os.path.join(checkpoints_path, file_name), "w") as f:
        f.write(data)


def read_json_file(path: str) -> dict | list:
    with open(path, "r") as f:
        return json.load(f)


def read_json_file_if_exists(path: str) -> dict | list:
    if os.path.exists(path):
        return read_json_file(path)
    return {}


def get_content_hash(content: str) -> str:
    """Compute SHA256 hash of a file."""
    sha = hashlib.sha256()
    sha.update(content.encode("utf-8"))
    return sha.hexdigest()


class Embedder:
    def __init__(self):
        pass

    def embed_query(self, text: str) -> list[float]:

        resp = requests.post(
            # url="http://127.0.0.1:1234/v1/embeddings",
            url="http://192.168.254.48:1234/v1/embeddings",

            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "model": "text-embedding-qwen3-embedding-0.6b",
                "input": text
            })
        ).json()
        return resp["data"][0]["embedding"]
