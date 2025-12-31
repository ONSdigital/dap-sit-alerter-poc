from functools import wraps

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, request, json, Request
from werkzeug.exceptions import Unauthorized

from app.dependabot_handler import DependabotHandler


# TODO: Code smell
def dependabot_handler_patch_setup_helper(
        send_to_teams_result: bool = True,
        slo_days: dict | None = None,
        channel_name: str | None = None,
):
    if slo_days is None:
        slo_days = {
            "critical": 5,
            "high": 15,
            "medium": 60,
        }

    if channel_name is None:
        channel_name = "teams"

    def decorator(test_func):
        @wraps(test_func)
        def wrapper(*args, **kwargs):
            mock_slo_config = MagicMock()
            mock_slo_config.slo_days = slo_days

            mock_notification_channels_config = MagicMock()
            mock_notification_channels_config.slo_days = channel_name

            with (
                patch.object(DependabotHandler, "_verify_security"),
                patch.object(DependabotHandler, "is_valid_action"),
                patch("app.dependabot_handler.SloConfig", return_value=mock_slo_config),
                patch("app.dependabot_handler.NotificationChannelsConfig", return_value=mock_notification_channels_config),
                patch("app.dependabot_handler.DependabotService.process_alert", return_value=send_to_teams_result),
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
    response, status_code = handler.handle_webhook(mock_req)

    # assert
    assert status_code == 400
    assert response.json["error"] == "Empty JSON payload"


def test_handle_webhook_stops_on_empty_payload(handler, app):
    # arrange
    handler._verify_security = MagicMock()
    handler._is_valid_action = MagicMock()
    mock_request = MagicMock()
    mock_request.json = {}

    # act
    handler.handle_webhook(mock_request)

    # assert
    handler._verify_security.assert_called_once()
    handler._is_valid_action.assert_not_called()


@patch.object(DependabotHandler, "_verify_security")
def test_handle_webhook_returns_a_202_when_action_is_invalid(_mock_verify_security, handler, app):
    # arrange
    payload = MagicMock(spec=Request)
    payload.json = {"action": "Bonkyhort Cutiebrunch"}

    # act
    response, status_code = handler.handle_webhook(payload)

    # assert
    assert status_code == 202
    assert "ignored" in json.loads(response.data)["status"]


@patch('config.channels.notification_channels_config.NotificationChannelsConfig')
@patch('config.slo.dependabot_slo_config.SloConfig')
@patch('app.dependabot_handler.verify_github_secret', return_value=True)
def test_handle_webhook_stops_processing_when_a_payload_action_is_ignored(
        mock_verify_secret,
        mock_slo_config,
        mock_notification_channels_config,
        handler,
        app):
    # arrange
    handler.is_valid_action = MagicMock()
    mock_request = MagicMock()
    mock_request.json = {
        "action": "ignored_action"
    }

    # act
    handler.handle_webhook(mock_request)

    # assert
    mock_verify_secret.assert_called_once()
    handler.is_valid_action.assert_called_once_with("ignored_action")
    mock_slo_config.assert_not_called()
    mock_notification_channels_config.assert_not_called()


@patch.object(DependabotHandler, "_verify_security")
@patch("app.dependabot_handler.SloConfig", side_effect=Exception("Bumblesniff Cumberpitch is too spicy"))
def test_load_slo_config_returns_500_when_config_is_invalid(_mock_load_slo, _mock_verify_security, handler, app, valid_payload):
    # act
    response, status_code = handler.handle_webhook(valid_payload)

    # assert
    assert status_code == 500
    assert response.json["error"] == "Invalid configuration"


@patch.object(DependabotHandler, "_verify_security")
@patch.object(DependabotHandler, "is_valid_action", return_value=True)
@patch("app.dependabot_handler.SloConfig")
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
    mock_load_slo_config.side_effect = Exception("Burberry Curdledmilk is too spicy")

    # act
    handler.handle_webhook(payload)

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
    response, status_code = handler.handle_webhook(valid_payload)

    # assert
    assert status_code == 502
    assert response.json["error"] == "Failed to send alert"


@dependabot_handler_patch_setup_helper()
def test_handle_webhook_returns_successful_response(
        handler,
        app,
        valid_payload
):
    # act
    response, status_code = handler.handle_webhook(valid_payload)

    # assert
    assert status_code == 200
    assert json.loads(response.data) == {"status": "ok"}


@patch.object(DependabotHandler, "_verify_security")
@patch.object(DependabotHandler, "is_valid_action")
@patch("app.dependabot_handler.SloConfig", return_value=MagicMock())
@patch("app.dependabot_handler.NotificationChannelsConfig", return_value=MagicMock())
@patch("app.dependabot_handler.DependabotService.process_alert", return_value=MagicMock())
def test_handle_webhook_calls_all_dependencies_when_successful(
    mock_notification_process_alert,
    mock_notification_channels_config,
    mock_slo_config,
    mock_is_valid_action,
    mock_verify_security,
    app,
    handler
):
    # arrange
    mock_request = MagicMock()
    mock_request.json = {
        "action": "created",
        "data": "example"
    }

    # act
    handler.handle_webhook(mock_request)

    # assert
    mock_verify_security.assert_called_once()
    mock_is_valid_action.assert_called_once_with("created")
    mock_slo_config.assert_called_once()
    mock_notification_channels_config.assert_called_once()
    mock_notification_process_alert.assert_called_once_with({
        "action": "created",
        "data": "example"
    })
