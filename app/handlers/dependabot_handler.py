import os

from flask import abort, Request

from app.auth import verify_github_signature, verify_github_event
from src.helpers import load_sla_config
from src.dependabot.dependabot_alert_model import DependabotAlert
from src.teams.teams_card_builder import TeamsCardBuilder
from src.teams.teams_notifier import send_to_teams


class Response:
    def __init__(self, status: int, body: str):
        self.status = status
        self.body = body


class DependabotHandler:
    def handle_webhook(self, payload: Request, teams_connector_url: str) -> Response:
        # security
        secret = os.environ.get('GITHUB_WEBHOOK_SECRET')
        if not verify_github_signature(secret):
            abort(401, description="Unauthorised")

        if not verify_github_event():
            abort(401, description="Unauthorised")

        payload = payload.json

        # validate action, i.e., created, reopened, fixed, etc

        # load config
        # TODO: Defensive programming.  Values cannot be 0/null/None, etc, and test it
        sla_config = load_sla_config()

        # parse alert
        alert = DependabotAlert.from_webhook(payload)

        # build Teams card
        teams_card_builder = TeamsCardBuilder(sla_config)
        teams_card = teams_card_builder.build_card(alert)

        # send to Teams
        success = send_to_teams(teams_card, teams_connector_url)

        if not success:
            return Response(400, f"Failed to send alert to Teams")

        return Response(200, f"Alert {alert.alert_number} sent to Teams")
