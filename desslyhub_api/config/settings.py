from dataclasses import dataclass

DEFAULT_BASE_URL = "https://desslyhub.com"
DEFAULT_TIMEOUT_SECONDS = 30.0


@dataclass(frozen=True, slots=True)
class ClientConfig:
    """Параметры подключения клиента: ключ, секрет, базовый URL и таймаут запроса."""

    api_key: str
    secret: str
    base_url: str = DEFAULT_BASE_URL
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS

    def __post_init__(self) -> None:
        """Проверяет, что API-ключ и секрет заданы и не пусты."""
        if not self.api_key:
            raise ValueError("API-ключ DesslyHub не может быть пустым")
        if not self.secret:
            raise ValueError("Секретный ключ DesslyHub не может быть пустым")
