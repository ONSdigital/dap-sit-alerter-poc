from typing import Dict, Any

from config.path_resolver import resolve_default_path
from config.yaml_loader import load_yaml


class SloConfig:
    def __init__(self, path: str = None):
        self.path = path or resolve_default_path("DEPENDABOT_SLO_CONFIG_PATH")

        # TODO: test dis
        if self.path is None:
            raise ValueError("No Service Level Objective (SLO) config path provided or found")

        self.raw = load_yaml(str(self.path))
        self._slo_days = self._extract_slo_days(self.raw)
        self._validate_slo_days(self._slo_days)

    @property
    def slo_days(self) -> Dict[str, int]:
        return self._slo_days

    @staticmethod
    def _extract_slo_days(raw_config: Dict[str, Any]) -> Dict[str, int]:
        if "slo_days" not in raw_config:
            raise ValueError("'slo_days' key not found in config")

        slo_days = raw_config["slo_days"]

        if not isinstance(slo_days, dict) or not slo_days:
            raise ValueError("slo_days must be a non-empty dictionary")

        return slo_days

    @staticmethod
    def _validate_slo_days(slo_days: Dict[str, int]):
        for priority, days in slo_days.items():
            if not isinstance(priority, str) or not priority.strip():
                raise ValueError(f"Invalid priority key {priority}. Priority must be a string")
            if not isinstance(days, int) or days <= 0:
                raise ValueError(f"Invalid days key {days} for priority {priority}. Days must be a positive integer")