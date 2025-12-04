import pytest

from handlers.incoming_request import build_teams_dependabot_card


def test_build_teams_dependabot_card_returns_expected_payload(incoming_github_dependabot_webhook, outgoing_microsoft_connector_card):
    # arrange & act
    result = build_teams_dependabot_card(incoming_github_dependabot_webhook)

    # assert
    assert type(result) == type(outgoing_microsoft_connector_card)