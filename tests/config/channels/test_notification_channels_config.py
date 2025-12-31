from config.channels.notification_channels_config import NotificationChannelsConfig


def test_channel_name_returns_expected_channel_name(notification_channels_config_path):
    # arrange
    notification_channels_config = NotificationChannelsConfig(notification_channels_config_path)

    # act
    result = notification_channels_config.channel_name

    # assert
    assert result == "slack"


def test_webhook_url_returns_expected_webhook_url_for_a_given_channel(notification_channels_config_path):
    # arrange
    notification_channels_config = NotificationChannelsConfig(notification_channels_config_path)

    # act
    result = notification_channels_config.webhook_url

    # assert
    assert result == "${SLACK_WEBHOOK_URL}"