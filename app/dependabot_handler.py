import logging
import os

from flask import abort, Request, jsonify
from flask.typing import ResponseReturnValue

from app.auth import verify_github_secret, verify_github_event
from src.dependabot.dependabot_alert_model import DependabotAlert
from src.factories.notifier_factory import NotifierFactory
from src.models.slo_config_model import load_slo_config
from src.factories.payload_factory import PayloadBuilderFactory


class DependabotHandler:
    def handle_webhook(self, payload: Request, teams_connector_url: str) -> ResponseReturnValue:
        self._verify_security()

        payload = payload.json
        if not payload:
            return jsonify({"error": "Empty JSON payload"}), 400

        action = payload.get("action", "NOT FOUND")
        if not self._is_valid_action(action):
            return jsonify({"status": "ignored", "reason": f"Action {action} not processed"}), 202

        if not self._load_slo_config():
            return jsonify({"error": "Invalid SLO config"}), 500

        alert = DependabotAlert.from_webhook(payload)

        # TODO: To be extracted behind a factory
        # build Teams payload
        teams_payload = TeamsPayloadBuilder(self.slo_config).build_payload(alert)

        notifier = NotifierFactory.get_notifier("teams")
        if not notifier.send(payload, teams_connector_url):
            return jsonify({"error": f"Failed to send alert to Teams"}), 502

        return jsonify({"status": "ok"}), 200

    @staticmethod
    def _verify_security():
        secret = os.environ.get('GITHUB_WEBHOOK_SECRET')
        if not verify_github_secret(secret):
            abort(401, description="Unauthorised")
        if not verify_github_event():
            abort(401, description="Unauthorised")

    @staticmethod
    def _is_valid_action(action: str) -> bool:
        return action in ["auto_reopened", "created", "reintroduced", "reopened"]

    def _load_slo_config(self) -> bool:
        try:
            self.slo_config = load_slo_config()
            return True
        except Exception as err:
            logging.error(f"Invalid SLO config: {err}")
            return False
