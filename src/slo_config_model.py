from dataclasses import dataclass
from typing import Dict


@dataclass
class SLOConfig:
    slo_days: Dict[str, int]

    def __post_init__(self):
        if not isinstance(self.slo_days, dict) or not self.slo_days:
            raise ValueError("slo_days must be a non-empty dictionary")

        for priority, days in self.slo_days.items():
            if not isinstance(priority, str) or not priority.strip():
                raise ValueError(f"Invalid priority key {priority}. Priority must be a string")
            if not isinstance(days, int) or days <= 0:
                raise ValueError(f"Invalid days key {days} for priority {priority}. Days must be a positive integer")