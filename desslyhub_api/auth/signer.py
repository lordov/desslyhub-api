import hashlib
import hmac
import time


def build_auth_headers(api_key: str, secret: str, body: str = "") -> dict[str, str]:
    """Формирует заголовки аутентификации с подписью HMAC-SHA256 для запроса.

    Алгоритм подписи: HMAC-SHA256(secret, api_key + timestamp + body).
    Timestamp — Unix-время в секундах. При пустом теле подписывается пустая строка.
    """
    timestamp = str(int(time.time()))
    message = api_key + timestamp + body
    signature = hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return {
        "X-Api-Key": api_key,
        "X-Timestamp": timestamp,
        "X-Signature": signature,
    }
