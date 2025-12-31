import logging
import os

from flask import abort, Request, jsonify
from flask.typing import ResponseReturnValue

from app.auth import verify_github_secret, verify_github_event
from config.channels.notification_channels_config import NotificationChannelsConfig
from config.slo.dependabot_slo_config import SloConfig
from src.dependabot.dependabot_service import DependabotService


class DependabotHandler:
    def __init__(self, secret: str = None):
        self.secret = secret or os.environ.get("GITHUB_WEBHOOK_SECRET")
        self.valid_actions = ["auto_reopened", "created", "reintroduced", "reopened"]

    def handle_webhook(self, payload: Request) -> ResponseReturnValue:
        self._verify_security()

        payload = payload.json
        if not payload:
            return jsonify({"error": "Empty JSON payload"}), 400

        action = payload.get("action", "NOT FOUND")
        if not self.is_valid_action(action):
            return jsonify({"status": "ignored", "reason": f"Action {action} not processed"}), 202

        try:
            slo_config = SloConfig()
            notification_config = NotificationChannelsConfig()
        except Exception as err:
            logging.error(f"Config loading failed: {err}")
            return jsonify({"error": "Invalid configuration"}), 500

        service = DependabotService(slo_config, notification_config)

        if not service.process_alert(payload):
            return jsonify({"error": "Failed to send alert"}), 502

        return jsonify({"status": "ok"}), 200

    def is_valid_action(self, action: str) -> bool:
        return action in self.valid_actions

    @staticmethod
    def _verify_security():
        secret = os.environ.get('GITHUB_WEBHOOK_SECRET')
        if not verify_github_secret(secret):
            abort(401, description="Unauthorised")
        if not verify_github_event():
            abort(401, description="Unauthorised")


