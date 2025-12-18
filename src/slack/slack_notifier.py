import logging

from src.factories.notifier_base import Notifier


class SlackNotifier(Notifier):
    def send(self, payload: dict, connector_url: str) -> bool:
        logging.info(f"Sending alert to Slack: {payload}")
        return True