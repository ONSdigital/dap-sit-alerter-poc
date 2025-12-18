import json
from unittest.mock import patch, MagicMock

import pytest
from dotenv import load_dotenv
from flask import Response, Flask

from app.endpoints import add_header, incoming

load_dotenv()

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TEAMS_CONNECTOR_URL'] = "http://dummy-url"
    app.register_blueprint(incoming)
    return app

@pytest.fixture
def client(app):
    return app.test_client()


def test_add_header_configures_the_response_headers_per_security_guidance():
    # arrange
    response = Response()

    # act
    response = add_header(response)

    # assert
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Strict-Transport-Security"] == "max-age=86400; includeSubDomains"
    assert response.headers["Cache-Control"] == "no-store"
    assert response.headers["Pragma"] == "no-cache"
    assert response.headers["Content-Security-Policy"] == "default-src 'self'"
    assert response.headers["X-Frame-Options"] == "DENY"


def test_health_check(client):
    # act
    response = client.get("/health")

    # assert
    assert json.loads(response.get_data(as_text=True)) == {"healthy": True}
    assert response.status_code == 200


@patch("app.endpoints.DependabotHandler")
def test_webhook_calls_handle_webhook_with_the_correct_parameters(
        mock_handler,
        incoming_github_dependabot_webhook,
        client
):
    # arrange
    mock_instance = MagicMock()
    mock_instance.handle_webhook.return_value = Response("ok", 200)
    mock_handler.return_value = mock_instance

    # act
    response = client.post("/webhook", json=incoming_github_dependabot_webhook)

    # assert
    mock_instance.handle_webhook.assert_called_once()

    args, kwargs = mock_instance.handle_webhook.call_args
    assert args[1] == "http://dummy-url"
    assert response.status_code == 200
    assert response.data == b"ok"
