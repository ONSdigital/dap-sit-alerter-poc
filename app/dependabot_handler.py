import logging
import os

from flask import abort, Request, jsonify
from flask.typing import ResponseReturnValue

from app.auth import verify_github_signature, verify_github_event
from src.dependabot.dependabot_alert_model import DependabotAlert
from src.models.slo_config_model import load_slo_config
from src.teams.teams_card_builder import TeamsCardBuilder
from src.teams.teams_notifier import send_to_teams


class DependabotHandler:
    def handle_webhook(self, payload: Request, teams_connector_url: str) -> ResponseReturnValue:
        # security
        secret = os.environ.get('GITHUB_WEBHOOK_SECRET')
        if not verify_github_signature(secret):
            abort(401, description="Unauthorised")

        if not verify_github_event():
            abort(401, description="Unauthorised")

        # arrange
        payload = payload.json
        if not payload:
            return jsonify({"error": "Empty JSON payload"}), 400

        # validate action
        action = payload.get("action", "NOT FOUND")
        if action not in ["auto_reopened", "created", "reintroduced", "reopened"]:
            return jsonify({"status": "ignored", "reason": f"Action {action} not processed"}), 202

        # load SLO config
        try:
            slo_config = load_slo_config()
        except Exception as err:
            logging.error(f"Invalid SLO config: {err}")
            return jsonify({"error": "Invalid SLO config"}), 500

        # parse alert
        alert = DependabotAlert.from_webhook(payload)

        # TODO: To be extracted behind a configureable notifier interface
        # build Teams card
        teams_card_builder = TeamsCardBuilder(slo_config)
        teams_card = teams_card_builder.build_card(alert)

        # send to Teams
        success = send_to_teams(teams_card, teams_connector_url)

        if not success:
            return jsonify({"error": f"Failed to send alert to Teams"}), 502

        return jsonify({"status": "ok"}), 200
