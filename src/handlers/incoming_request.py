from dataclasses import asdict
from typing import Dict

from src.models.dependabot_webhook_model import DependabotAlert
from src.models.ms_teams_card_model import OutgoingMessageCard, Section, Fact, PotentialAction, ActionTarget


def build_teams_dependabot_card(incoming_payload: Dict):
    alert = incoming_payload.get("alert", {})

    # dependabot url
    dependabot_url = alert.get("html_url", {})

    # package_name
    dependency = alert.get("dependency", {})
    package = dependency.get("package", {})
    ecosystem = package.get("ecosystem")

    # severity_level
    # security_advisory = alert.get("security_advisory", {})
    # severity_level = security_advisory.get("severity", {})

    # theme colour
    critical = "E81123" # red
    medium = "FFA500"   # orange
    low = "FFEB3B"      # yellow

    # repository
    repository = incoming_payload.get("repository", {})
    repository_full_name = repository.get("full_name")

    # refactored
    alert = DependabotAlert.from_dict(incoming_payload)

    package_name = alert.package.name
    severity_level = alert.severity_level

    outgoing_payload = OutgoingMessageCard(
        summary=f"Dependabot Alert: {package_name} ({severity_level.capitalize()} severity)",
        theme_colour=critical,
        title=f"🚨 Dependabot Alert: {severity_level.capitalize()} Severity Vulnerability Detected 🚨",
        sections=[
            Section(
                activity_title=f"**Repository:** {repository_full_name}",
                activity_subtitle="Dependabot has detected a new vulnerability",
                activity_image="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
            ),
            Section(
                title="**Vulnerability Details**",
                facts=[
                    Fact(name="Package", value=f"`{package_name}` ({ecosystem})"),
                    Fact(name="Severity", value=f"{severity_level.capitalize()}"),
                    Fact(name="Resolution timeframe", value="15 working days - due 31/01/2026"),
                ]
            ),
            Section(
                title="Useful Links",
                facts=[
                    Fact(
                        name="Dependabot Alert",
                        value=f"[View in GitHub]({dependabot_url})"
                    )
                ]
            ),
        ],
        potential_action=[
            PotentialAction(
                type="OpenUri",
                name="View Alert in GitHub",
                target=[
                    ActionTarget(
                        os="default",
                        uri=f"{dependabot_url}"
                    )
                ]
            )
        ]
    )

    return asdict(outgoing_payload)


# TODO: Test business days. Create an incoming payload with a configureable date. Test the output.