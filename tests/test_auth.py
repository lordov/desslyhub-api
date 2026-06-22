import hashlib
import hmac

import pytest

from desslyhub_api.auth.signer import build_auth_headers


@pytest.mark.parametrize(
    "body",
    ["", '{"amount":1}'],
)
def test_build_auth_headers_signature(body: str) -> None:
    """Заголовки содержат корректную HMAC-SHA256 подпись api_key+timestamp+body."""
    headers = build_auth_headers("api-key", "secret", body)

    expected_message = "api-key" + headers["X-Timestamp"] + body
    expected_signature = hmac.new(
        b"secret", expected_message.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    assert headers["X-Api-Key"] == "api-key"
    assert headers["X-Signature"] == expected_signature


def test_build_auth_headers_default_empty_body() -> None:
    """При отсутствии тела подписывается пустая строка."""
    headers = build_auth_headers("api-key", "secret")

    expected_message = "api-key" + headers["X-Timestamp"]
    expected_signature = hmac.new(
        b"secret", expected_message.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    assert headers["X-Signature"] == expected_signature
    assert headers["X-Timestamp"].isdigit()
