from typing import Any, Dict


class DependabotWebhook:
    def __init__(self, payload: Dict[str, Any]):
        self.payload = payload

        self.alert = payload.get('alert')

        self.dependency = self.alert.get('dependency')
        self.package = self.dependency.get('package')

    @property
    def package_name(self):
        return self.package.get('name')