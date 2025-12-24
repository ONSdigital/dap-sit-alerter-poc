import pytest

from app.app import setup_app


@pytest.fixture
def incoming_github_dependabot_webhook():
    return {
      "action": "created",
      "alert": {
        "number": 42,
        "html_url": "https://github.com/your-org/your-repo/security/dependabot/42",
        "created_at": "2025-11-30T14:23:00Z",
        "auto_dismissed_at": None,
        "dismissed_at": None,
        "dismissed_by": None,
        "dismissed_reason": None,
        "dismissed_comment": None,
        "fixed_at": None,
        "dependency": {
          "manifest_path": "package-lock.json",
          "package": {
            "ecosystem": "npm",
            "name": "lodash"
          },
          "scope": "runtime"
        },
        "security_advisory": {
          "cve_id": "CVE-2025-1234",
          "ghsa_id": "GHSA-xxxx-xxxx-xxxx",
          "summary": "Prototype pollution in lodash < 4.17.21",
          "description": "Versions of lodash before 4.17.21 are vulnerable to Prototype Pollution.",
          "severity": "high",
          "cvss": {
            "score": 7.5,
            "vector_string": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H"
          },
          "identifiers": [
            {
              "type": "CVE",
              "value": "CVE-2025-1234"
            }
          ],
          "references": [
            {
              "url": "https://nvd.nist.gov/vuln/detail/CVE-2025-1234"
            }
          ]
        }
      },
      "repository": {
        "id": 12345678,
        "name": "your-repo",
        "full_name": "your-org/your-repo",
        "private": False,
        "html_url": "https://github.com/your-org/your-repo",
        "owner": {
          "login": "your-org",
          "id": 87654321,
          "type": "Organization"
        }
      },
      "organization": {
        "login": "your-org",
        "id": 87654321,
        "type": "Organization"
      },
      "installation": {
        "id": 101112,
        "account": {
          "login": "your-org",
          "id": 87654321,
          "type": "Organization"
        }
      },
      "sender": {
        "login": "dependabot[bot]",
        "id": 78901234,
        "type": "Bot"
      }
    }


@pytest.fixture
def outgoing_microsoft_connector_card_payload():
    return {
        "contentType": "application/vnd.microsoft.teams.card.o365connector",
        "content": {
          "@type": "MessageCard",
          "@context": "https://schema.org/extensions",
          "summary": "Dependabot Alert: lodash (High severity)",
          "themeColour": "F7630C",
          "title": "🚨 Dependabot Alert: High Severity Vulnerability Detected 🚨",
          "sections": [
            {
              "activityTitle": "**Repository:** your-org/your-repo",
              "activitySubtitle": "Dependabot has detected a new vulnerability",
              "activityImage": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
            },
            {
              "title": "**Vulnerability Details**",
              "facts": [
                {
                  "name": "Package",
                  "value": "`lodash` (npm)"
                },
                {
                  "name": "Severity",
                  "value": "High"
                },
                {
                  "name": "Resolution timeframe",
                  "value": "15 working days - due 16/02/2026"
                },
              ],
            },
            {
              "title": "Useful Links",
              "facts": [
                {
                  "name": "Dependabot Alert",
                  "value": "[View in GitHub](https://github.com/your-org/your-repo/security/dependabot/42)"
                },
              ]
            }
          ],
          "potentialAction": [
            {
              "@type": "OpenUri",
              "name": "View Alert in GitHub",
              "target": [
                { "os": "default", "uri": "https://github.com/your-org/your-repo/security/dependabot/42" }
              ]
            }
          ]
        }
    }


@pytest.fixture
def outgoing_slack_payload():
  return {
  "channel": "C0123456789", # Slack channel ID
  "text": "🚨 Dependabot Alert: lodash (High severity)",
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "🚨 Dependabot Alert: High Severity Vulnerability Detected 🚨",
        "emoji": True
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Repository:* <https://github.com/your-org/your-repo|your-org/your-repo>\n*Detected by:* Dependabot"
      },
      "accessory": {
        "type": "image",
        "image_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
        "alt_text": "GitHub"
      }
    },
    {
      "type": "divider"
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*Package*\n`lodash` (npm)"
        },
        {
          "type": "mrkdwn",
          "text": "*Severity*\n*High*"
        },
      ]
    },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "style": "danger",
          "text": {
            "type": "plain_text",
            "text": "View Alert in GitHub"
          },
          "url": "https://github.com/your-org/your-repo/security/dependabot/42"
        }
      ]
    },
    {
      "type": "context",
      "elements": [
        {
          "type": "mrkdwn",
          "text": "Resolution timeframe: 15 working days - due 16/02/2026"
        }
      ]
    }
  ]
}


@pytest.fixture
def app():
    return setup_app()


@pytest.fixture
def client(app):
    return app.test_client()
