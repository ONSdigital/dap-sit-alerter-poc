import logging
from typing import Dict, Any

import requests

from src.models.response_model import Response


# TODO: Create custom Teams Card type
def send_to_teams(card: Dict[str, Any], teams_connector_url: str):
    print("Posting connector card to Teams...")
    import json
    print(json.dumps(card, indent=4))
    return Response(200, "OK")

    # headers = {'Content-Type': 'application/json'}
    # response = requests.post(
    #     teams_connector_url, json=card, headers=headers)
    # return response.status_code
