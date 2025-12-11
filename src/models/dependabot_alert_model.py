from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class DependabotAlert:
    package_name: str
    severity_level: str
    repository_fullname: str
    package_ecosystem: str
    created_date: str
    dependabot_url: str

    @classmethod
    def from_webhook(cls, payload: Dict[str, Any]):
        # TODO: Is defaulting to None the desired behaviour when it can't be found?
        # TODO: created_date and severity_level are dependencies
        alert = payload.get("alert", {})
        dependency = alert.get("dependency", {})
        package = dependency.get("package", {})

        security_advisory = alert.get("security_advisory", {})

        repository = payload.get("repository", {})

        return cls(
            package_name=package.get("name"),
            severity_level=security_advisory.get("severity"),
            repository_fullname=repository.get("full_name"),
            package_ecosystem=package.get("ecosystem"),
            created_date=alert.get("created_at"),
            dependabot_url=alert.get("html_url"),
        )


