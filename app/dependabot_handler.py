import logging
import os

from flask import abort, Request

from app.auth import verify_github_signature, verify_github_event
from src.helpers import load_slo_config
from src.dependabot.dependabot_alert_model import DependabotAlert
from src.models.response_model import Response
from src.models.slo_config_model import SLOConfig
from src.teams.teams_card_builder import TeamsCardBuilder
from src.teams.teams_notifier import send_to_teams


class DependabotHandler:
    def handle_webhook(self, payload: Request, teams_connector_url: str) -> Response:
        # security
        secret = os.environ.get('GITHUB_WEBHOOK_SECRET')
        if not verify_github_signature(secret):
            abort(401, description="Unauthorised")

        if not verify_github_event():
            abort(401, description="Unauthorised")

        # arrange
        payload = payload.json
        if not payload:
            return Response(400, "Empty JSON payload")

        # validate action
        action = payload.get("action", "NOT FOUND")
        if action not in ["auto_reopened", "created", "reintroduced", "reopened"]:
            return Response(204, f"Action {action} not processed")

        # load config
        try:
            raw_config = load_slo_config()
            slo_config = SLOConfig(**raw_config)
        except Exception as err:
            logging.error(f"Invalid SLO config: {err}")
            return Response(500, "Invalid SLO config")

        # parse alert
        alert = DependabotAlert.from_webhook(payload)

        # build Teams card
        teams_card_builder = TeamsCardBuilder(slo_config)
        teams_card = teams_card_builder.build_card(alert)

        # send to Teams
        success = send_to_teams(teams_card, teams_connector_url)

        if not success:
            return Response(400, f"Failed to send alert to Teams")

        return Response(200, f"Alert {alert.alert_number} sent to Teams")
