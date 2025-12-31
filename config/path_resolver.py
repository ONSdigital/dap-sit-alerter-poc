import os
from pathlib import Path


def resolve_default_path(env_var: str) -> Path:
    env_path = os.getenv(env_var)
    if env_path:
        return Path(env_path)
