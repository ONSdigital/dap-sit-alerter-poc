from dataclasses import dataclass, field, asdict
from typing import List, Optional

@dataclass
class Fact:
    name: str
    value: str


@dataclass
class Section:
    activity_image: str = field(default="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png")
    activity_subtitle: Optional[str] = None
    title: Optional[str] = None
    facts: Optional[List[Fact]] = None
    activity_title: Optional[str] = None


@dataclass
class ActionTarget:
    os: str
    uri: str


@dataclass
class PotentialAction:
    name: str
    type: str = field(metadata={"json_key": "@type"})
    target: List[ActionTarget] = field(default_factory=list)


@dataclass
class OutgoingMessageCard:
    summary: str
    theme_colour: str
    title: str
    sections: List[Section]
    potential_action: List[PotentialAction]

    type: str = field(default="MessageCard", metadata={"json_key": "@type"})
    context: str = field(default="https://schema.org/extensions", metadata={"json_key": "@context"})


@dataclass
class ConnectorEnvelope:
    content: OutgoingMessageCard
    content_type: str = "application/vnd.microsoft.teams.card.o365connector"



def build_teams_dependabot_card(payload):
    payload = OutgoingMessageCard(
        summary="Dependabot Alert: lodash (High severity)",
        theme_colour="E81123",
        title="🚨 Dependabot Alert: High Severity Vulnerability Detected 🚨",
        sections=[
            Section(
                activity_title="**Repository:** your-org/your-repo",
                activity_subtitle="Dependabot has detected a new vulnerability",
                activity_image="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
            ),
            Section(
                title="**Vulnerability Details**",
                facts=[
                    Fact(name="Package", value="`lodash` (npm)"),
                    Fact(name="Severity", value="High"),
                    Fact(name="Resolution timeframe", value="15 working days - due 31/01/2026"),
                ]
            ),
            Section(
                title="Useful Links",
                facts=[
                    Fact(
                        name="Dependabot Alert",
                        value="[View in GitHub](https://github.com/your-org/your-repo/security/dependabot/42)"
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
                        uri="https://github.com/your-org/your-repo/security/dependabot/42"
                    )
                ]
            )
        ]
    )

    return asdict(payload)