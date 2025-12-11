from typing import Dict, Any

import yaml
from pathlib import Path


def load_sla_config(path: str = None) -> Dict[str, Any]:
    if path is None:
        project_root = Path(__file__).resolve().parents[1]
        path = project_root / "dependabot_sla.yml"

    with open(path, "r") as file:
        config = yaml.safe_load(file)
    return config["sla_days"]