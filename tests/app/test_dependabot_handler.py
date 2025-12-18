import pytest
from unittest.mock import Mock, patch
from flask import Flask, request, json

from app.dependabot_handler import DependabotHandler


@pytest.fixture
def flask_request():
    app = Flask(__name__)
    payload = {"action": "created", "alert": {"id": 123}}
    with app.test_request_context("/webhook", method="POST", json=payload):
        yield request


@patch("app.dependabot_handler.send_to_teams", return_value=True)
@patch("app.dependabot_handler.TeamsCardBuilder")
@patch("app.dependabot_handler.DependabotAlert.from_webhook")
@patch("app.dependabot_handler.load_slo_config")
@patch("app.dependabot_handler.verify_github_event", return_value=True)
@patch("app.dependabot_handler.verify_github_signature", return_value=True)
def test_handle_webhook_happy_path(
        _mock_verify_signature,
        _mock_verify_event,
        mock_load_slo,
        mock_from_webhook,
        mock_card_builder_cls,
        mock_send_to_teams,
        flask_request
):
    # arrange
    handler = DependabotHandler()
    fake_slo_config = {"some": "config"}
    fake_alert = Mock()
    fake_teams_card = {"title": "Alert!"}

    mock_load_slo.return_value = fake_slo_config
    mock_from_webhook.return_value = fake_alert
    mock_card_builder = mock_card_builder_cls.return_value
    mock_card_builder.build_card.return_value = fake_teams_card

    # act
    response, status_code = handler.handle_webhook(flask_request, "https://teams.connector.url")

    # assert
    assert status_code == 200
    assert json.loads(response.data) == {"status": "ok"}
    mock_card_builder_cls.assert_called_once_with(fake_slo_config)
    mock_card_builder.build_card.assert_called_once_with(fake_alert)
    mock_send_to_teams.assert_called_once_with(fake_teams_card, "https://teams.connector.url")
