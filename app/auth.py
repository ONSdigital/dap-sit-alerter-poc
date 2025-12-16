from typing import Optional

from flask import current_app
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username: str, password: str) -> Optional[str]:
    if current_app.config["user"] == username and check_password_hash(
        current_app.config["password_hash"], password
    ):
        return username
    return None
