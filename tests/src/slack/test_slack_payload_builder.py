from src.dependabot.dependabot_alert_model import DependabotAlert
from src.models.slo_config_model import load_slo_config
from src.slack.slack_payload_builder import SlackPayloadBuilder


def test_build_slack_payload_returns_expected_payload(incoming_github_dependabot_webhook,
                                                      outgoing_slack_payload):
    # arrange
    config = load_slo_config()
    payload = SlackPayloadBuilder(config)

    incoming_github_dependabot_webhook["alert"]["created_at"] = "2026-01-26T00:00:00Z"
    alert = DependabotAlert.from_webhook(incoming_github_dependabot_webhook)

    # act
    result = payload.build_payload(alert)

    # assert
    assert result == outgoing_slack_payload


def test_build_slack_payload_returns_expected_number_and_order_of_blocks(incoming_github_dependabot_webhook):
    # arrange
    config = load_slo_config()
    payload = SlackPayloadBuilder(config)

    incoming_github_dependabot_webhook["alert"]["created_at"] = "2026-01-26T00:00:00Z"
    alert = DependabotAlert.from_webhook(incoming_github_dependabot_webhook)

    # act
    result = payload.build_payload(alert)["blocks"]

    # assert
    assert result[0]["type"] == "header"
    assert result[1]["type"] == "section"
    assert result[2]["type"] == "divider"
    assert result[3]["type"] == "section"
    assert result[4]["type"] == "actions"
    assert result[5]["type"] == "context"
