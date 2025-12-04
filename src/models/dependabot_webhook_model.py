from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class SecurityAdvisoryBlock:
    severity: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(severity=data.get("severity"))


@dataclass
class DependencyBlock:
    name: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(name=data.get("name"))


@dataclass
class DependabotAlert:
    severity: SecurityAdvisoryBlock
    package: DependencyBlock

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]):
        severity = SecurityAdvisoryBlock.from_dict(payload.get("security_advisory", {}))
        package = DependencyBlock.from_dict(payload.get("package", {}))

        return cls(
            severity=severity,
            package=package,
        )
