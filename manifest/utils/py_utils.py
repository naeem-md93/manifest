import yaml
from pathlib import Path


def mkdir(path: Path) -> bool:
    try:
        if path.is_dir():
            path.mkdir(parents=True, exist_ok=True)
            return True
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            return True
    except Exception as e:
        print(str(e))
        return False

def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def read_text_file(file_path: Path) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_text_file(file_path: Path, content: str) -> bool:

    mkdir(file_path)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False

def append_text_file(file_path: Path, content: str) -> bool:

    mkdir(file_path)

    try:
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False
