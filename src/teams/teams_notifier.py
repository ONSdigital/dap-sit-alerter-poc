from typing import Dict, Any


# TODO: Create custom Teams payload type
def send_to_teams(payload: Dict[str, Any], teams_connector_url: str):
    """
    This function has been stubbed until integration details with Teams has been authorised and configured
    """
    print("Posting connector card to Teams...")
    import json
    print(json.dumps(payload, indent=4))
    return True
