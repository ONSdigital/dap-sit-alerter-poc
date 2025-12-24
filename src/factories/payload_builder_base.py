from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta

from src.dependabot.dependabot_alert_model import DependabotAlert


class PayloadBuilder(ABC):
    @abstractmethod
    def build_payload(self, alert: DependabotAlert):
        pass

    def _get_formatted_deadline_string(self, alert: DependabotAlert) -> str:
        created_date_input = datetime.strptime(alert.created_date, "%Y-%m-%dT%H:%M:%SZ")
        created_date = created_date_input.date()

        severity_level = alert.severity_level.lower()
        if severity_level not in self.slo_config:
            raise ValueError(f"Unknown severity level: {severity_level}")

        working_days = self.slo_config[severity_level]

        due_date = self._get_deadline_date(created_date, working_days)

        return f"{working_days} working days - due {due_date.strftime('%d/%m/%Y')}"

    def _get_severity_colour(self, severity_level: str) -> str:
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

    def _get_deadline_date(self, start_date: date, days: int) -> date:
        days_added = 0
        while days_added < days:
            start_date += timedelta(days=1)
            if start_date.weekday() < 5:
                days_added += 1
        return start_date