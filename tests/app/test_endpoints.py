import json

from dotenv import load_dotenv

load_dotenv()


def assert_security_headers_are_present(response):
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Strict-Transport-Security"] == "max-age=86400; includeSubDomains"
    assert response.headers["Cache-Control"] == "no-store"
    assert response.headers["Pragma"] == "no-cache"
    assert response.headers["Content-Security-Policy"] == "default-src 'self'"
    assert response.headers["X-Frame-Options"] == "DENY"


def test_health_check(client):
    # act
    response = client.get("/health")

    # assert
    assert json.loads(response.get_data(as_text=True)) == {"healthy": True}
    assert response.status_code == 200
    assert_security_headers_are_present(response)
