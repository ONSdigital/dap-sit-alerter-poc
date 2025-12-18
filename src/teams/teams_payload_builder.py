from datetime import datetime, date, timedelta
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

    def _get_formatted_deadline_string(self, alert: DependabotAlert) -> str:
        created_date_input = datetime.strptime(alert.created_date, "%Y-%m-%dT%H:%M:%SZ")
        created_date = created_date_input.date()

        severity_level = alert.severity_level.lower()
        if severity_level not in self.slo_config:
            raise ValueError(f"Unknown severity level: {severity_level}")

        working_days = self.slo_config[severity_level]

        due_date = self._get_deadline_date(created_date, working_days)

        return f"{working_days} working days - due {due_date.strftime('%d/%m/%Y')}"

    @staticmethod
    def _get_severity_colour(severity_level: str) -> str:
        severity_colours = {
            'critical': 'E81123',   # red
            'high': 'F7630C',       # strong orange
            'medium': 'FFA500',     # orange
            'low': 'FFEB3B',        # yellow
            'unknown': '9E8E9E'     # millenial grey
        }
        if type(severity_level) != str:
            return severity_colours['unknown']

        return severity_colours.get(severity_level.lower(), severity_colours['unknown'])

    @staticmethod
    def _get_deadline_date(start_date: date, days: int) -> date:
        days_added = 0
        while days_added < days:
            start_date += timedelta(days=1)
            if start_date.weekday() < 5:
                days_added += 1
        return start_date

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
