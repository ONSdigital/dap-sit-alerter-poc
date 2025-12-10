from src.handlers.incoming_request import build_teams_dependabot_card
from src.models.dependabot_webhook_model import DependabotWebhook


def test_build_teams_dependabot_card_returns_expected_payload(incoming_github_dependabot_webhook, outgoing_microsoft_connector_card):
    # arrange
    output = outgoing_microsoft_connector_card
    expected_output = outgoing_microsoft_connector_card["content"]

    # act
    result = build_teams_dependabot_card(incoming_github_dependabot_webhook)

    # assert
    assert result == expected_output


def test_dependabot_webhook_model_returns_expected_package_name(incoming_github_dependabot_webhook):
    # arrange
    dependabot_webhook = DependabotWebhook(incoming_github_dependabot_webhook)

    # act
    result = dependabot_webhook.package_name

    # assert
    assert result == "lodash"
