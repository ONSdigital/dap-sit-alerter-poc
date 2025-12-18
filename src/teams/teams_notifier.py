from typing import Dict, Any


# TODO: Create custom Teams Card type
def send_to_teams(card: Dict[str, Any], teams_connector_url: str):
    print("Posting connector card to Teams...")
    import json
    print(json.dumps(card, indent=4))
    return True

    # headers = {'Content-Type': 'application/json'}
    # response = requests.post(
    #     teams_connector_url, json=card, headers=headers)
    # return response.status_code
