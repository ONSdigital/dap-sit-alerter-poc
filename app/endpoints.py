import logging
import os

from flask import Blueprint, jsonify, request, abort

from app.auth import verify_github_signature, verify_github_event
from src.helpers import load_sla_config
from src.models.dependabot_alert_model import DependabotAlert
from src.services.outgoing import send_to_teams
from src.services.teams_card_builder import TeamsCardBuilder

incoming = Blueprint("endpoints", __name__)

@incoming.after_request
def add_header(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers['Strict-Transport-Security'] = 'max-age=86400; includeSubDomains'
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["X-Frame-Options"] = "DENY"
    return response


@incoming.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200


@incoming.route('/webhook', methods=['POST'])
def webhook():
    logging.info("Incoming GitHub webhook")

    secret = os.environ.get('GITHUB_WEBHOOK_SECRET')
    if not verify_github_signature(secret):
        abort(401, description="Unauthorised")

    if not verify_github_event():
        abort(401, description="Unauthorised")

    payload = request.json

    # TODO: Refactor - handler pattern
    alert = DependabotAlert.from_webhook(payload)

    # TODO: Defensive programming.  Values cannot be 0/null/None, etc, and test it
    sla_config = load_sla_config()

    # TODO: Configure output channel, i.e., Teams, Slack, email, fax, etc
    teams_card_builder = TeamsCardBuilder(sla_config)
    teams_card = teams_card_builder.build_card(alert)

    return send_to_teams(teams_card)
