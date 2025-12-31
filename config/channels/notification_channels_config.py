from config.path_resolver import resolve_default_path
from config.yaml_loader import load_yaml


class NotificationChannelsConfig:
    def __init__(self, path: str = None):
        self.path = path or resolve_default_path("NOTIFICATION_CHANNELS_CONFIG_PATH")
        self.raw = load_yaml(str(self.path))

    @property
    def channel_name(self):
        return next((name for name, cfg in self.raw.items() if cfg.get("enabled")), None)

    @property
    def webhook_url(self):
        return self.raw[self.channel_name]["webhook_url"]

