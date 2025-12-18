from src.factories.payload_builder_base import PayloadBuilder
from src.teams.teams_payload_builder import TeamsPayloadBuilder


class PayloadBuilderFactory:
    @staticmethod
    # TODO: move slo_config extraction here
    # TODO: create custom type for slo_config
    # TODO: Use Type Var for return type???
    def get_payload_builder(notifier_channel: str, slo_config) -> "PayloadBuilder":
        if notifier_channel.lower() == "teams":
            return TeamsPayloadBuilder(slo_config)

        if notifier_channel.lower() == "slack":
            return PayloadBuilder()
