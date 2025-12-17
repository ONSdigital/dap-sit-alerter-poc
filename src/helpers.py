from typing import Dict, Any

import yaml
from pathlib import Path


# TODO: Move this to the SLO Config model
def load_slo_config(path: str = None) -> Dict[str, Any]:
    if path is None:
        project_root = Path(__file__).resolve().parents[1]
        path = project_root / "config" / "dependabot_slo.yml"

    with open(path, "r") as file:
        config = yaml.safe_load(file)
    return config["slo_days"]