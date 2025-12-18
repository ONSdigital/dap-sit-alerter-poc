import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, request, json, Request
from werkzeug.exceptions import Unauthorized

from app.dependabot_handler import DependabotHandler


@pytest.fixture
def flask_request():
    app = Flask(__name__)
    payload = {"action": "created", "alert": {"id": 123}}
    with app.test_request_context("/webhook", method="POST", json=payload):
        yield request


@pytest.fixture
def handler():
    return DependabotHandler()


@pytest.fixture(scope="session")
def app():
    app = Flask(__name__)
    with app.app_context():
        yield app


@patch("app.dependabot_handler.send_to_teams", return_value=True)
@patch("app.dependabot_handler.TeamsCardBuilder")
@patch("app.dependabot_handler.DependabotAlert.from_webhook")
@patch("app.dependabot_handler.load_slo_config")
@patch("app.dependabot_handler.verify_github_event", return_value=True)
@patch("app.dependabot_handler.verify_github_secret", return_value=True)
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



@patch("app.dependabot_handler.verify_github_secret", return_value=False)
@patch("app.dependabot_handler.verify_github_event", return_value=True)
def test_verify_security_aborts_with_invalid_secret(_mock_event, _mock_secret):
    # act & assert
    with pytest.raises(Unauthorized):
        DependabotHandler._verify_security()


@patch("app.dependabot_handler.verify_github_secret", return_value=True)
@patch("app.dependabot_handler.verify_github_event", return_value=False)
def test_verify_security_aborts_with_invalid_event(_mock_event, _mock_secret):
    # act & assert
    with pytest.raises(Unauthorized):
        DependabotHandler._verify_security()


@patch("app.dependabot_handler.verify_github_secret", return_value=True)
@patch("app.dependabot_handler.verify_github_event", return_value=True)
def test_handle_webhook_returns_400_when_payload_is_empty(_mock_event, _mock_secret, handler):
    # arrange
    mock_req = MagicMock(spec=Request)
    mock_req.json = None

    # act
    response, status_code = handler.handle_webhook(mock_req, "dummy_url")

    # assert
    assert status_code == 400
    assert response.json["error"] == "Empty JSON payload"


@patch.object(DependabotHandler, "_verify_security")
def test_handle_webhook_returns_a_202_when_action_is_invalid(_mock_verify_security, handler, app):
    # arrange
    payload = MagicMock(spec=Request)
    payload.json = {"action": "Bonkyhort Cutiebrunch"}

    # act
    response, status_code = handler.handle_webhook(payload, "dummy_url")

    # assert
    assert status_code == 202
    assert "ignored" in json.loads(response.data)["status"]
