from typing import Dict, Any

from src.dependabot.dependabot_alert_model import DependabotAlert
from src.factories.payload_builder_base import PayloadBuilder


class SlackPayloadBuilder(PayloadBuilder):
    def __init__(self, slo_config: Dict[str, int]) -> None:
        self.slo_config = slo_config

    def build_payload(self, alert: DependabotAlert) -> Dict[str, Any]:
        return {
  "channel": "C0123456789", # Slack channel ID
  "text": f"🚨 Dependabot Alert: {alert.package_name} ({alert.severity_level.capitalize()} severity)",
  "blocks": self._build_payload_blocks(alert)
}

    def _build_payload_blocks(self, alert: DependabotAlert):
      return [
        self._header_block(alert),
        self._repository_block(alert),
        self._divider(),
        self._package(alert),
        self._actions(alert),
        self._resolution_timeframe(alert)
      ]

    def _resolution_timeframe(self, alert):
      return {
        "type": "context",
        "elements": [
          {
            "type": "mrkdwn",
            "text": f"Resolution timeframe: {self._get_formatted_deadline_string(alert)}"
          }
        ]
      }

    def _actions(self, alert):
      return {
        "type": "actions",
        "elements": [
          {
            "type": "button",
            "style": "danger",
            "text": {
              "type": "plain_text",
              "text": "View Alert in GitHub"
            },
            "url": f"{alert.dependabot_url}"
          }
        ]
      }

    def _package(self, alert):
      return {
        "type": "section",
        "fields": [
          {
            "type": "mrkdwn",
            "text": f"*Package*\n`{alert.package_name}` ({alert.package_ecosystem})"
          },
          {
            "type": "mrkdwn",
            "text": f"*Severity*\n*{alert.severity_level.capitalize()}*"
          },
        ]
      }

    def _divider(self):
      return {
        "type": "divider"
      }

    def _repository_block(self, alert: DependabotAlert):
      return {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": f"*Repository:* <{alert.repository_url}|{alert.repository_fullname}>\n*Detected by:* Dependabot"
        },
        "accessory": {
          "type": "image",
          "image_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
          "alt_text": "GitHub"
        }
      }

    def _header_block(self, alert):
      return {
        "type": "header",
        "text": {
          "type": "plain_text",
          "text": f"🚨 Dependabot Alert: {alert.severity_level.capitalize()} Severity Vulnerability Detected 🚨",
          "emoji": True
        }
      }
