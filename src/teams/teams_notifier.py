from typing import Dict, Any

import requests

# TODO: Create custom Teams Card type
def send_to_teams(card: Dict[str, Any], teams_connector_url: str):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(
        teams_connector_url, json=card, headers=headers)
    return response.status_code
