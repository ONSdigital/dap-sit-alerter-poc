from abc import ABC, abstractmethod


class Notifier(ABC):
    @abstractmethod
    def send(self, payload: dict, connector_url: str) -> bool:
        pass