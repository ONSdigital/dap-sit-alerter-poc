import pytest

from unittest.mock import patch
from datetime import date

from src.dependabot.dependabot_alert_model import DependabotAlert
from src.models.slo_config_model import load_slo_config
from src.teams.teams_card_builder import TeamsCardBuilder



def test_build_card_returns_expected_payload(incoming_github_dependabot_webhook, outgoing_microsoft_connector_card):
    # arrange
    config = load_slo_config()
    card = TeamsCardBuilder(config)

    incoming_github_dependabot_webhook["alert"]["created_at"] = "2026-01-26T00:00:00Z"
    alert = DependabotAlert.from_webhook(incoming_github_dependabot_webhook)

    # act
    result = card.build_card(alert)

    # assert
    assert result == outgoing_microsoft_connector_card


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


@patch("src.models.slo_config_model.load_slo_config")
@patch("src.teams.teams_card_builder.TeamsCardBuilder._get_deadline_date")
def test_get_formatted_deadline_string_returns_expected_string(mock_get_due, mock_load_slo, incoming_github_dependabot_webhook):
    # arrange
    incoming_github_dependabot_webhook["alert"]["security_advisory"]["severity"] = "critical"
    alert = DependabotAlert.from_webhook(incoming_github_dependabot_webhook)

    config = load_slo_config()
    card = TeamsCardBuilder(config)

    mock_load_slo.return_value={"critical": 5}
    mock_get_due.return_value=date(2025, 12, 31)

    # act
    result = card._get_formatted_deadline_string(alert)

    # assert
    assert result == "5 working days - due 31/12/2025"


def test_get_formatted_deadline_string_raises_value_error_when_severity_level_is_invalid():
    # arrange
    config = load_slo_config()
    card = TeamsCardBuilder(config)
    alert = DependabotAlert(
        severity_level="BUTTERNUT_CRINKLEFRIES!!!",
        package_name="lodash",
        package_ecosystem="npm",
        repository_fullname="your-org/your-repo",
        created_date="2025-12-11T12:00:00Z",
        dependabot_url="https://github.com/your-org/your-repo/security/dependabot/42",
    )

    # act & assert
    with pytest.raises(ValueError) as exception_info:
        card._get_formatted_deadline_string(alert)

    assert str(exception_info.value) == "Unknown severity level: butternut_crinklefries!!!"


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


def test_get_deadline_date_skips_weekends():
    # arrange
    card = TeamsCardBuilder
    friday = date(2025, 12, 26)
    monday = date(2025, 12, 29)
    days_to_resolve = 1

    # act
    result = card._get_deadline_date(start_date= friday, days=days_to_resolve)

    # assert
    assert result == monday


@pytest.mark.parametrize(
    "package_name, package_ecosystem, expected_package_field",
    [
        ("weird^name*&$", "weird$eco-system$$$", "`weird^name*&$` (weird$eco-system$$$)"),
        ("", "npm", "`` (npm)"),                               # empty package name
        ("lodash", "", "`lodash` ()"),                         # empty ecosystem
        ("", "", "`` ()"),                                    # both empty
        ("🔥britishname-complicated🌵", "✨bustamove cumberdance🧪", "`🔥britishname-complicated🌵` (✨bustamove cumberdance🧪)"),
    ]
)
def test_build_vulnerability_details_returns_expected_payload_with_unusual_or_empty_fields(package_name, package_ecosystem, expected_package_field):
    # arrange
    config = load_slo_config()
    card = TeamsCardBuilder(config)

    alert = DependabotAlert(
        severity_level="high",
        package_name=package_name,
        package_ecosystem=package_ecosystem,
        repository_fullname="your-org/your-repo",
        created_date="2025-12-11T12:00:00Z",
        dependabot_url="https://github.com/your-org/your-repo/security/dependabot/42",
    )

    # act
    package_details = card._build_vulnerability_details(alert)
    result = package_details[0]

    # assert
    assert result["name"] == "Package"
    assert result["value"] == expected_package_field


def test_build_useful_links_returns_expected_markdown():
    # arrange
    config = load_slo_config()
    card = TeamsCardBuilder(config)

    alert = DependabotAlert(
        dependabot_url="https://github.com/bondadonk/cumbernoodle/security/dependabot/100",
        severity_level="high",
        package_name="lodash",
        package_ecosystem="npm",
        repository_fullname="your-org/your-repo",
        created_date="2025-12-11T12:00:00Z",
    )

    # act
    useful_links = card._build_useful_links(alert)
    result = useful_links[0]

    # assert
    # TODO: update behaviour to return more useful message if url is not available
    assert result["value"] == "[View in GitHub](https://github.com/bondadonk/cumbernoodle/security/dependabot/100)"


def test_build_card_sections_handles_missing_or_malformed_fields():
    # arrange
    config = load_slo_config()
    card = TeamsCardBuilder(config)

    alert = DependabotAlert(
        package_name="",
        package_ecosystem="",
        repository_fullname="",
        dependabot_url="",
        created_date="2025-12-11T12:00:00Z",
        severity_level="high",
    )

    # act
    result = card._build_card_sections(alert)

    # assert
    assert isinstance(result, list)
    assert len(result) == 3


def test_build_card_sections_returns_expected_structure():
    # arrange
    config = load_slo_config()
    card = TeamsCardBuilder(config)

    alert = DependabotAlert(
        package_name="lodash",
        package_ecosystem="npm",
        repository_fullname="your-org/your-repo",
        dependabot_url="https://github.com/org/repo/security/1",
        created_date="2025-12-11T12:00:00Z",
        severity_level="high",
    )

    # act
    result = card._build_card_sections(alert)

    # assert
    assert len(result) == 3

    repository_section, vulnerability_section, links_section = result

    assert "activityTitle" in repository_section
    assert "**Repository:** your-org/your-repo" in repository_section["activityTitle"]
    assert repository_section["activitySubtitle"] == "Dependabot has detected a new vulnerability"
    assert repository_section["activityImage"].startswith("https://github.githubassets.com")

    assert vulnerability_section["title"] == "**Vulnerability Details**"
    assert isinstance(vulnerability_section["facts"], list)
    assert len(vulnerability_section["facts"]) >= 3

    assert links_section["title"] == "Useful Links"
    assert isinstance(links_section["facts"], list)
    assert len(links_section["facts"]) == 1
    assert "View in GitHub" in links_section["facts"][0]["value"]
