import pytest

from unittest.mock import patch
from datetime import date

from src.models.dependabot_alert_model import DependabotAlert
from src.services.teams_card_builder import TeamsCardBuilder
from src.helpers import load_sla_config


@pytest.mark.parametrize(
    "severity_level, expected_hex",
    [
        ("critical", "E81123"),                 # red
        ("high", "F7630C"),                     # strong orange
        ("medium", "FFA500"),                   # orange
        ("low", "FFEB3B"),                      # yellow
        ("unknown", "9E8E9E"),                  # grey
        ("CRITICAL", "E81123"),                 # red
        ("High", "F7630C"),                     # strong orange
        ("mEdIuM", "FFA500"),                   # orange
        ("lOw", "FFEB3B"),                      # yellow
        ("uNKNOWn", "9E8E9E"),                  # grey
        ("Benadryl Cabbagepatch", "9E8E9E"),    # grey
        (None, "9E8E9E"),                       # grey
        ("", "9E8E9E"),                         # grey
        (123456789, "9E8E9E"),                  # grey
    ],
)
def test_get_severity_colour_returns_expected_hex_colour(severity_level, expected_hex):
    # arrange
    card = TeamsCardBuilder

    # act
    result = card._get_severity_colour(severity_level)

    # assert
    assert result == expected_hex


@pytest.mark.parametrize(
    "days_to_resolve, expected_date_to_resolve",
    [
        (5, date(2026, 1, 1)),    # critical
        (15, date(2026, 1, 15)),  # high
        (60, date(2026, 3, 19)),  # med/moderate
        (90, date(2026, 4, 30)),  # low
    ]
)
def test_get_deadline_date_returns_expected_date(days_to_resolve, expected_date_to_resolve):
    # arrange
    card = TeamsCardBuilder

    # act
    result = card._get_deadline_date(start_date= date(2025, 12, 25), days=days_to_resolve)

    # assert
    assert result == expected_date_to_resolve


@patch("src.helpers.load_sla_config")
@patch("src.services.teams_card_builder.TeamsCardBuilder._get_deadline_date")
def test_format_resolution_deadline_date_returns_expected_string(mock_get_due, mock_load_sla, incoming_github_dependabot_webhook):
    # arrange
    incoming_github_dependabot_webhook["alert"]["security_advisory"]["severity"] = "critical"
    alert = DependabotAlert.from_webhook(incoming_github_dependabot_webhook)

    config = load_sla_config()
    card = TeamsCardBuilder(config)

    mock_load_sla.return_value={"critical": 5}
    mock_get_due.return_value=date(2025, 12, 31)

    # act
    result = card._get_formatted_deadline_string(alert)

    # assert
    assert result == "5 working days - due 31/12/2025"


def test_build_card_returns_expected_payload(incoming_github_dependabot_webhook, outgoing_microsoft_connector_card):
    # arrange
    config = load_sla_config()
    card = TeamsCardBuilder(config)

    incoming_github_dependabot_webhook["alert"]["created_at"] = "2026-01-26T00:00:00Z"
    alert = DependabotAlert.from_webhook(incoming_github_dependabot_webhook)

    # act
    result = card.build_card(alert)

    # assert
    assert result == outgoing_microsoft_connector_card
