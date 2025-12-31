from config.slo.dependabot_slo_config import SloConfig
from src.dependabot.dependabot_alert_model import DependabotAlert
from src.slack.slack_payload_builder import SlackPayloadBuilder
from tests.helpers import write_yaml


def test_build_slack_payload_returns_expected_payload(incoming_github_dependabot_webhook,
                                                      outgoing_slack_payload, tmp_path, config_dictionary):
    # arrange
    path = write_yaml(tmp_path, config_dictionary)
    slo_config = SloConfig(path)

    payload = SlackPayloadBuilder(slo_config.slo_days)

    incoming_github_dependabot_webhook["alert"]["created_at"] = "2026-01-26T00:00:00Z"
    alert = DependabotAlert.from_webhook(incoming_github_dependabot_webhook)

    # act
    result = payload.build_payload(alert)

    # assert
    assert result == outgoing_slack_payload


def test_build_slack_payload_returns_expected_number_and_order_of_blocks(incoming_github_dependabot_webhook, tmp_path, config_dictionary):
    # arrange
    path = write_yaml(tmp_path, config_dictionary)
    slo_config = SloConfig(path)

    payload = SlackPayloadBuilder(slo_config.slo_days)

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
