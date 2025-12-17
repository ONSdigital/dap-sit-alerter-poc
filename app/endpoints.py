import logging

from flask import Blueprint, jsonify, request, current_app

from app.dependabot_handler import DependabotHandler


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
    return jsonify({'healthy': True}), 200


@incoming.route('/webhook', methods=['POST'])
def webhook():
    logging.info("Incoming GitHub webhook")
    return DependabotHandler().handle_webhook(request, current_app.config['TEAMS_CONNECTOR_URL'])
