import logging

from config.channels.notification_channels_config import NotificationChannelsConfig
from config.slo.dependabot_slo_config import SloConfig
from src.dependabot.dependabot_alert_model import DependabotAlert
from src.factories.notifier_factory import NotifierFactory
from src.factories.payload_factory import PayloadBuilderFactory

# TODO: Test dis
class DependabotService:
    def __init__(self, slo_config: SloConfig, notification_config: NotificationChannelsConfig):
        self.slo_config = slo_config
        self.notification_config = notification_config

    def process_alert(self, payload: dict) -> bool:
        alert = DependabotAlert.from_webhook(payload)
        notification_payload  = self._build_notification_payload(alert)
        return self._send_notification(notification_payload)

    def _build_notification_payload(self, alert: DependabotAlert) -> dict:
        payload_builder = PayloadBuilderFactory.get_payload_builder(
            self.notification_config.channel_name,
            self.slo_config.slo_days
        )
        return payload_builder.build_payload(alert)

    def _send_notification(self, notification_payload):
        notifier = NotifierFactory.get_notifier(self.notification_config.channel_name)
        success = notifier.send(notification_payload, self.notification_config.webhook_url)
        if not success:
            logging.error(f"Failed to send alert to {self.notification_config.channel_name}")
        return success
