from src.notifier_base import Notifier


class TeamsNotifier(Notifier):
    def send(self, payload: dict, connector_url: str) -> bool:
        """
        This function has been stubbed until integration details with Teams has been authorised and configured
        """
        print("Posting connector card to Teams...")
        import json
        print(json.dumps(payload, indent=4))
        return True
