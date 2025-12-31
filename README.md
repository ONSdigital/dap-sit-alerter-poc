# DAP SIT Alerter POC

POC middleware to forward GitHub Dependabot alerts to Microsoft Teams with automated slo tracking.

## Features
* Receives GitHub Dependabot webhook events
* Converts alerts into configurable channels such as Microsoft Teams or Slack
* Automatically calculates resolution deadlines based on the [ONS GitHub Policy](https://officenationalstatistics.sharepoint.com/:w:/r/sites/knexPolicies/_layouts/15/Doc.aspx?sourcedoc=%7B89725180-4A87-41CA-958C-B60806E32895%7D&file=GitHub%20Usage%20Policy.docx&wdOrigin=TEAMS-MAGLEV.null_ns.rwc&action=default&mobileredirect=true) (on-net documenation, soz!)
* Fully unit-testable Python codebase
* Configurable via environment variables

## What is the SLO?
The SLO (Service Level Objective) in this project defines the maximum number of days allowed to resolve a Dependabot alert based on its priority, per the [ONS GitHub Policy](https://officenationalstatistics.sharepoint.com/:w:/r/sites/knexPolicies/_layouts/15/Doc.aspx?sourcedoc=%7B89725180-4A87-41CA-958C-B60806E32895%7D&file=GitHub%20Usage%20Policy.docx&wdOrigin=TEAMS-MAGLEV.null_ns.rwc&action=default&mobileredirect=true). The SLO is configurable via the config/slo/dependabot_slo.yml file, for example:
```yaml
slo_days:
  critical: 5
  high: 15
  medium: 60
  moderate: 60
  low: 90
```
These values indicate the number of working days to resolve alerts for each priority level.

The handler uses this SLO to automatically calculate the deadlines for each incoming Dependabot alert and include them in the alert.

## Setup

1. Clone the repository
```bash
git clone https://github.com/your-org/dap-sit-alert-poc.git
cd dap-sit-alert-poc
```

2. Install dependencies with Poetry
```bash
poetry install
```

3. Activate the virtual environment
```bash
poetry shell
```

4. Create a '.env' file in the project root, and configure the environment variables:
```bash
TEAMS_CONNECTOR_URL=https://example.com/test-webhook
GITHUB_WEBHOOK_SECRET=your-webhook-secret-here
```
#### Optional: Override SLO configuration location
By default, the application loads the SLO configuration from:
```
config/slo/dependabot_slo.yml
```

If you need to override this, i.e., in CI, Docker or production, set:
```
DEPENDABOT_SLO_CONFIG_PATH=/absolute/path/to/dependabot_slo.yml
```

**Note:** Do not commit `.env` Git. Do not pass Go. Do not collect £200. `.env` is already included in `.gitignore`

## Running Unit Tests
Tests use ```pytest```. To run all tests:
```bash
poetry run pytest
```

Or, if inside the Poetry shell:
```bash
pytest
```

You can run tests with verbose output:
```bash
pytest -v
```

## References and Credits
This project draws inspiration from and builds on the approach described in [Leveraging Webhooks to Integrate GitHub Advanced Security Events with Microsoft Teams — A Step by Step Tutorial](https://medium.com/%40federicomadotto/leveraging-webhooks-to-integrate-github-advanced-security-events-with-microsoft-teams-a-step-by-a13790e7d688) by Federico Madotto.