from typing import Dict, Any


# TODO: Create custom Teams Card type
def send_to_teams(card: Dict[str, Any], teams_connector_url: str):
    """
    This function has been stubbed until integration details with Teams has been authorised and configured
    """
    print("Posting connector card to Teams...")
    import json
    print(json.dumps(card, indent=4))
    return True
