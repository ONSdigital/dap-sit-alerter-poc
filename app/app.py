import os

from flask import Flask

from app.endpoints import incoming


def setup_app():
    teams_url = os.environ.get('TEAMS_CONNECTOR_URL')
    if not teams_url:
        raise ValueError('TEAMS_CONNECTOR_URL environment variable is required')

    app = Flask(__name__)
    app.register_blueprint(incoming)
    app.config['TEAMS_CONNECTOR_URL'] = teams_url

    return app
