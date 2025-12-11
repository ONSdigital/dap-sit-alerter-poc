from src.models.dependabot_alert_model import DependabotAlert


def test_dependabot_alert_returns_expected_package_name(incoming_github_dependabot_webhook):
    # arrange & act
    alert = DependabotAlert.from_webhook(incoming_github_dependabot_webhook)

    # assert
    assert alert.package_name == "lodash"


def test_dependabot_alert_returns_expected_severity_level(incoming_github_dependabot_webhook):
    # arrange & act
    alert = DependabotAlert.from_webhook(incoming_github_dependabot_webhook)

    # assert
    assert alert.severity_level == "high"


def test_dependabot_alert_returns_expected_repository_fullname(incoming_github_dependabot_webhook):
    # arrange & act
    alert = DependabotAlert.from_webhook(incoming_github_dependabot_webhook)

    # assert
    assert alert.repository_fullname == "your-org/your-repo"


def test_dependabot_alert_returns_expected_package_ecosystem(incoming_github_dependabot_webhook):
    # arrange & act
    alert = DependabotAlert.from_webhook(incoming_github_dependabot_webhook)

    # assert
    assert alert.package_ecosystem == "npm"