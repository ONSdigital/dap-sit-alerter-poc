import pytest

from app.app import setup_app


# TODO: Review this behaviour.  If notifier channel is Slack, there's no need for a Teams connector
def test_setup_app_raises_value_error_when_teams_connector_is_not_configured(monkeypatch):
    # arrange
    monkeypatch.delenv('TEAMS_CONNECTOR_URL', False)

    # act & assert
    with pytest.raises(ValueError, match="TEAMS_CONNECTOR_URL environment variable is required"):
        setup_app()


def test_setup_app_creates_flask_app(monkeypatch):
    # arrange
    monkeypatch.setenv("TEAMS_CONNECTOR_URL", "http://dummy-url")

    # act
    app = setup_app()

    # assert
    assert app.config['TEAMS_CONNECTOR_URL'] == "http://dummy-url"
