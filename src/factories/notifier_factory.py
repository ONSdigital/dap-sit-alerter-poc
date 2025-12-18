from src.slack.slack_notifier import SlackNotifier
from src.teams.teams_notifier import TeamsNotifier


class NotifierFactory:
    @staticmethod
    def get_notifier(notifier_type: str) -> "Notifier":
        notifier_type = notifier_type.lower()

        if notifier_type.lower() == "teams":
            return TeamsNotifier()

        if notifier_type.lower() == "slack":
            return SlackNotifier()