import pytest

from desslyhub_api.config.settings import (
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT_SECONDS,
    ClientConfig,
)


def test_client_config_defaults() -> None:
    """Конфигурация использует базовый URL и таймаут по умолчанию."""
    config = ClientConfig(api_key="key", secret="secret")

    assert config.base_url == DEFAULT_BASE_URL
    assert config.timeout_seconds == DEFAULT_TIMEOUT_SECONDS


def test_client_config_custom_values() -> None:
    """Конфигурация сохраняет переданные значения ключа, секрета, URL и таймаута."""
    config = ClientConfig(
        api_key="key",
        secret="secret",
        base_url="https://example.com",
        timeout_seconds=5.0,
    )

    assert config.api_key == "key"
    assert config.secret == "secret"
    assert config.base_url == "https://example.com"
    assert config.timeout_seconds == 5.0


@pytest.mark.parametrize(
    ("api_key", "secret", "message"),
    [
        ("", "secret", "API-ключ"),
        ("key", "", "Секретный ключ"),
    ],
)
def test_client_config_rejects_empty_credentials(api_key: str, secret: str, message: str) -> None:
    """Пустой API-ключ или секрет приводит к ValueError с понятным сообщением."""
    with pytest.raises(ValueError, match=message):
        ClientConfig(api_key=api_key, secret=secret)
