import logging

from flask import Flask, request, jsonify

from src.helpers import load_sla_config
from src.models.dependabot_alert_model import DependabotAlert
from src.services.outgoing import send_to_teams
from src.services.teams_card_builder import TeamsCardBuilder

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    logging.info("Incoming GitHub webhook")
    payload = request.json

    # TODO: Refactor - handler pattern
    alert = DependabotAlert.from_webhook(payload)

    # TODO: Defensive programming.  Values cannot be 0/null/None, etc, and test it
    sla_config = load_sla_config()

    # TODO: Configure output channel, i.e., Teams, Slack, email, fax, etc
    teams_card_builder = TeamsCardBuilder(sla_config)
    teams_card = teams_card_builder.build_card(alert)

    return send_to_teams(teams_card)


