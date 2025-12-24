from src.dependabot.dependabot_alert_model import DependabotAlert


def test_dependabot_alert_returns_expected_package_name(incoming_github_dependabot_webhook):
    # arrange & act
    alert = DependabotAlert.from_webhook(incoming_github_dependabot_webhook)

    # assert
    assert alert.package_name == "lodash"


def test_dependabot_alert_returns_none_when_package_name_cannot_be_found():
    # arrange & act
    alert = DependabotAlert.from_webhook({})

    # assert
    assert alert.package_name is None


def test_dependabot_alert_returns_expected_severity_level(incoming_github_dependabot_webhook):
    # arrange & act
    alert = DependabotAlert.from_webhook(incoming_github_dependabot_webhook)

    # assert
    assert alert.severity_level == "high"


def test_dependabot_alert_returns_none_when_expected_severity_level_cannot_be_found():
    # arrange & act
    alert = DependabotAlert.from_webhook({})

    # assert
    assert alert.severity_level is None


def test_dependabot_alert_returns_expected_repository_fullname(incoming_github_dependabot_webhook):
    # arrange & act
    alert = DependabotAlert.from_webhook(incoming_github_dependabot_webhook)

    # assert
    assert alert.repository_fullname == "your-org/your-repo"


def test_dependabot_alert_returns_none_when_expected_repository_fullname_cannot_be_found():
    # arrange & act
    alert = DependabotAlert.from_webhook({})

    # assert
    assert alert.repository_fullname is None


def test_dependabot_alert_returns_expected_package_ecosystem(incoming_github_dependabot_webhook):
    # arrange & act
    alert = DependabotAlert.from_webhook(incoming_github_dependabot_webhook)

    # assert
    assert alert.package_ecosystem == "npm"


def test_dependabot_alert_returns_none_when_expected_package_ecosystem_cannot_be_found():
    # arrange & act
    alert = DependabotAlert.from_webhook({})

    # assert
    assert alert.package_ecosystem is None


def test_dependabot_alert_returns_expected_created_date(incoming_github_dependabot_webhook):
    # arrange & act
    alert = DependabotAlert.from_webhook(incoming_github_dependabot_webhook)

    # assert
    assert alert.created_date == "2025-11-30T14:23:00Z"


def test_dependabot_alert_returns_none_when_expected_created_date_cannot_be_found():
    # arrange & act
    alert = DependabotAlert.from_webhook({})

    # assert
    assert alert.created_date is None


def test_dependabot_alert_returns_expected_dependabot_url(incoming_github_dependabot_webhook):
    # arrange & act
    alert = DependabotAlert.from_webhook(incoming_github_dependabot_webhook)

    # assert
    assert alert.dependabot_url == "https://github.com/your-org/your-repo/security/dependabot/42"


def test_dependabot_alert_returns_none_when_expected_dependabot_url_cannot_be_found():
    # arrange & act
    alert = DependabotAlert.from_webhook({})

    # assert
    assert alert.dependabot_url is None


def test_dependabot_alert_returns_expected_repository_url(incoming_github_dependabot_webhook):
    # arrange & act
    alert = DependabotAlert.from_webhook(incoming_github_dependabot_webhook)

    # assert
    assert alert.repository_url == "https://github.com/your-org/your-repo"


def test_dependabot_alert_returns_none_when_expected_repository_url_cannot_be_found():
    # arrange & act
    alert = DependabotAlert.from_webhook({})

    # assert
    assert alert.repository_url is None
