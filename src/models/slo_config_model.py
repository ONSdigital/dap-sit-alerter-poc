import logging

import yaml

from pathlib import Path
from typing import Dict, Any


def load_slo_config(path: str = None) -> Dict[str, Any]:
    if path is None:
        project_root = Path(__file__).resolve().parents[2]
        path = project_root / "config" / "dependabot_slo.yml"

    try:
        with open(path, "r") as file:
            config = yaml.safe_load(file)
    except Exception as err:
        logging.error(f"Failed to load SLO config from {path}: {err}")
        raise

    # validate
    if "slo_days" not in config:
        raise ValueError("'slo_days' key not found in config")

    slo_days = config["slo_days"]

    if not isinstance(slo_days, dict) or not slo_days:
        raise ValueError("slo_days must be a non-empty dictionary")

    for priority, days in slo_days.items():
        if not isinstance(priority, str) or not priority.strip():
            raise ValueError(f"Invalid priority key {priority}. Priority must be a string")
        if not isinstance(days, int) or days <= 0:
            raise ValueError(f"Invalid days key {days} for priority {priority}. Days must be a positive integer")

    return config["slo_days"]
