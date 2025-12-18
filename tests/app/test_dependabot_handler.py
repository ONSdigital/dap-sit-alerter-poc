from functools import wraps

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, request, json, Request
from werkzeug.exceptions import Unauthorized

from app.dependabot_handler import DependabotHandler


def dependabot_handler_patch_setup_helper(send_to_teams_result: bool = True):
    def decorator(test_func):
        @wraps(test_func)
        def wrapper(*args, **kwargs):
            with (
                patch.object(DependabotHandler, "_verify_security"),
                patch("app.dependabot_handler.load_slo_config", return_value={"slo": "config"}),
                patch("app.dependabot_handler.DependabotAlert.from_webhook", return_value=MagicMock()),
                patch("app.dependabot_handler.TeamsCardBuilder"),
                patch("app.dependabot_handler.send_to_teams", return_value=send_to_teams_result),
            ):
                return test_func(*args, **kwargs)

        return wrapper
    return decorator


@pytest.fixture
def valid_payload():
    payload = MagicMock(spec=Request)
    payload.json = {
        "action": "created",
        "alert": {"id": 123},
    }
    return payload


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
def test_handle_webhook_returns_400_when_payload_is_empty(_mock_event, _mock_secret, handler, app):
    # arrange
    mock_req = MagicMock(spec=Request)
    mock_req.json = None

    # act
    response, status_code = handler.handle_webhook(mock_req, "dummy_url")

    # assert
    assert status_code == 400
    assert response.json["error"] == "Empty JSON payload"


@patch.object(DependabotHandler, "_verify_security")
@patch.object(DependabotHandler, "_is_valid_action")
@patch.object(DependabotHandler, "_load_slo_config")
def test_handle_webhook_stops_processing_when_an_empty_payload_is_sent(
        mock_load_slo_config,
        mock_is_valid_action,
        mock_verify_security,
        handler,
        app,
):
    # act
    payload = MagicMock(spec=Request)
    payload.json = {}

    handler.handle_webhook(payload, "dummy_url")

    # assert
    mock_verify_security.assert_called_once()
    mock_is_valid_action.assert_not_called()
    mock_load_slo_config.assert_not_called()


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


@patch.object(DependabotHandler, "_verify_security")
@patch.object(DependabotHandler, "_is_valid_action", return_value=False)
@patch.object(DependabotHandler, "_load_slo_config")
def test_handle_webhook_stops_processing_when_a_payload_action_is_ignored(
        mock_load_slo_config,
        mock_is_valid_action,
        mock_verify_security,
        handler,
        app,
):
    # arrange
    payload = MagicMock(spec=Request)
    payload.json = {"action": "Bonkyhort Cutiebrunch"}

    # act
    handler.handle_webhook(payload, "dummy_url")

    # assert
    mock_verify_security.assert_called_once()
    mock_is_valid_action.assert_called_once()
    mock_load_slo_config.assert_not_called()


@patch.object(DependabotHandler, "_verify_security")
@patch("app.dependabot_handler.load_slo_config", side_effect=Exception("Bumblesniff Cumberpitch is too spicy"))
def test_load_slo_config_returns_500_when_config_is_invalid(_mock_load_slo, _mock_verify_security, handler, app, valid_payload):
    # act
    response, status_code = handler.handle_webhook(valid_payload, "dummy_url")

    # assert
    assert status_code == 500
    assert response.json["error"] == "Invalid SLO config"


@patch.object(DependabotHandler, "_verify_security")
@patch.object(DependabotHandler, "_is_valid_action", return_value=True)
@patch.object(DependabotHandler, "_load_slo_config", return_value=False)
@patch("src.dependabot.dependabot_alert_model.DependabotAlert.from_webhook")
def test_handle_webhook_stops_processing_when_slo_config_is_invalid(
        mock_from_webhook,
        mock_load_slo_config,
        mock_is_valid_action,
        mock_verify_security,
        handler,
        app,
):
    # arrange
    payload = MagicMock(spec=Request)
    payload.json = {"action": "created"}

    # act
    handler.handle_webhook(payload, "dummy_url")

    # assert
    mock_verify_security.assert_called_once()
    mock_is_valid_action.assert_called_once_with("created")
    mock_load_slo_config.assert_called_once()
    mock_from_webhook.assert_not_called()


@dependabot_handler_patch_setup_helper(send_to_teams_result=False)
def test_handle_webhook_returns_502_when_an_alert_fails_to_send_to_teams(
        handler,
        app,
        valid_payload
):
    # act
    response, status_code = handler.handle_webhook(valid_payload, "dummy_url")

    # assert
    assert status_code == 502
    assert response.json["error"] == "Failed to send alert to Teams"


@dependabot_handler_patch_setup_helper()
def test_handle_webhook_returns_successful_response(
        handler,
        app,
        valid_payload
):
    # act
    response, status_code = handler.handle_webhook(valid_payload, "https://teams.connector.url")

    # assert
    assert status_code == 200
    assert json.loads(response.data) == {"status": "ok"}


# TODO: Code smell
@patch.object(DependabotHandler, "_verify_security")
@patch.object(DependabotHandler, "_is_valid_action", return_value=True)
@patch.object(DependabotHandler, "_load_slo_config", return_value=True)
@patch("app.dependabot_handler.DependabotAlert.from_webhook")
@patch("app.dependabot_handler.TeamsCardBuilder")
@patch("app.dependabot_handler.TeamsNotifier.send", return_value=True)
def test_handle_webhook_calls_call_dependencies_when_successful(
    mock_send_to_teams,
    mock_card_builder_cls,
    mock_from_webhook,
    mock_load_slo_config,
    mock_is_valid_action,
    mock_verify_security,
    handler,
    app,
    valid_payload
):
    # arrange
    fake_slo_config = MagicMock()
    fake_alert = MagicMock()
    fake_card = {"card": "data"}

    handler.slo_config = fake_slo_config
    mock_from_webhook.return_value = fake_alert

    card_builder = mock_card_builder_cls.return_value
    card_builder.build_card.return_value = fake_card

    # act
    handler.handle_webhook(valid_payload, "connector-url")

    # assert
    mock_verify_security.assert_called_once()
    mock_is_valid_action.assert_called_once_with("created")
    mock_load_slo_config.assert_called_once()

    mock_from_webhook.assert_called_once_with(valid_payload.json)
    mock_card_builder_cls.assert_called_once_with(fake_slo_config)
    card_builder.build_card.assert_called_once_with(fake_alert)

    mock_send_to_teams.assert_called_once_with(fake_card, "connector-url")
