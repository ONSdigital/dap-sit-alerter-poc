import logging

from flask import Flask, request

from handlers.incoming_request import build_teams_dependabot_card
from handlers.outgoing_request import send_to_teams

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    logging.info("Incoming webhook")

    payload = request.json
    teams_card = build_teams_dependabot_card(payload)
    return send_to_teams(teams_card)


