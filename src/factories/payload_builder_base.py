from abc import ABC, abstractmethod

from src.dependabot.dependabot_alert_model import DependabotAlert


class PayloadBuilder(ABC):
    @abstractmethod
    def build_payload(self, alert: DependabotAlert):
        pass