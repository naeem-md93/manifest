from pathlib import Path
from typing import Any
from pydantic import BaseModel


class ManifestState(BaseModel):
    is_finished: bool = False
    conversations: dict[str, list[dict[str, str]]] = {}
    messages: dict[str, list[dict[str, str]]] = {}
    documents: dict[str, list[str]] = {}

    cache_dir: Path = Path("./tmp/")
    history_path: Path = Path("./tmp/history.md")