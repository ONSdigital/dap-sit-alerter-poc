from typing import Dict, Any

from src.dependabot.dependabot_alert_model import DependabotAlert
from src.factories.payload_builder_base import PayloadBuilder


class TeamsPayloadBuilder(PayloadBuilder):
    def __init__(self, slo_config: Dict[str, int]) -> None:
        # TODO: Defensive programming and test
        self.slo_config = slo_config

    def build_payload(self, alert: DependabotAlert) -> Dict[str, Any]:
        return {
            "contentType": "application/vnd.microsoft.teams.card.o365connector",
            "content": {
                "@type": "MessageCard",
                "@context": "https://schema.org/extensions",
                "summary": f"Dependabot Alert: {alert.package_name} ({alert.severity_level.capitalize()} severity)",
                "themeColour": f"{self._get_severity_colour(alert.severity_level)}",
                "title": f"🚨 Dependabot Alert: {alert.severity_level.capitalize()} Severity Vulnerability Detected 🚨",
                "sections": self._build_payload_sections(alert),
                "potentialAction": self._build_potential_actions(alert)
            }
        }

    def _build_payload_sections(self, alert: DependabotAlert) -> list[dict[str, str]]:
        return [
            {
                "activityTitle": f"**Repository:** {alert.repository_fullname}",
                "activitySubtitle": "Dependabot has detected a new vulnerability",
                "activityImage": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
            },
            {
                "title": "**Vulnerability Details**",
                "facts": self._build_vulnerability_details(alert)
            },
            {
                "title": "Useful Links",
                "facts": self._build_useful_links(alert)
            }

        ]

    def _build_vulnerability_details(self, alert: DependabotAlert) -> list[dict[str, str]]:
        return [
            {
                "name": "Package",
                "value": f"`{alert.package_name}` ({alert.package_ecosystem})"
            },
            {
                "name": "Severity",
                "value": f"{alert.severity_level.capitalize()}"
            },
            {
                "name": "Resolution timeframe",
                "value": f"{self._get_formatted_deadline_string(alert)}"
            },
        ]

    @staticmethod
    def _build_useful_links(alert: DependabotAlert) -> list[dict[str, str]]:
        return [
            {
                "name": "Dependabot Alert",
                "value": f"[View in GitHub]({alert.dependabot_url})"
            }
        ]

    @staticmethod
    def _build_potential_actions(alert: DependabotAlert):
        return [
            {
                "@type": "OpenUri",
                "name": "View Alert in GitHub",
                "target": [
                    {
                        "os": "default",
                        "uri": f"{alert.dependabot_url}"
                    }
                ]
            }
        ]
