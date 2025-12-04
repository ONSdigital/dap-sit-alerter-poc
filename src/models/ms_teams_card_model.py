from dataclasses import dataclass, field
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