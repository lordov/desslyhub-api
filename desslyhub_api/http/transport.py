from types import TracebackType
from typing import Any

import aiohttp
import orjson

from desslyhub_api.auth.signer import build_auth_headers
from desslyhub_api.config.settings import ClientConfig
from desslyhub_api.errors.exceptions import (
    DesslyHubConnectionError,
    DesslyHubResponseError,
    raise_from_error_model,
)
from desslyhub_api.logger.logger import get_logger

logger = get_logger(__name__)


class HttpTransport:
    """Асинхронный транспорт: формирует запросы, парсит JSON и проверяет ошибки API."""

    def __init__(self, config: ClientConfig) -> None:
        """Сохраняет конфигурацию и подготавливает отложенную HTTP-сессию."""
        self._config = config
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "HttpTransport":
        """Открывает HTTP-сессию при входе в контекстный менеджер."""
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Закрывает HTTP-сессию при выходе из контекстного менеджера."""
        await self.close()

    async def start(self) -> None:
        """Создаёт постоянную HTTP-сессию для повторного использования."""
        if self._session is not None:
            return
        timeout = aiohttp.ClientTimeout(total=self._config.timeout_seconds)
        self._session = aiohttp.ClientSession(
            base_url=self._config.base_url,
            timeout=timeout,
        )

    async def close(self) -> None:
        """Закрывает HTTP-сессию, если она была открыта."""
        if self._session is None:
            return
        await self._session.close()
        self._session = None

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Выполняет HTTP-запрос и возвращает разобранный и проверенный ответ API."""
        status, raw = await self._send(method, path, params=params, json=json)
        payload = self._decode(raw)
        if status >= 400:
            logger.error("API DesslyHub вернул ошибку, HTTP-статус %s", status)
            raise_from_error_model(status, payload)
        return payload

    async def _send(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None,
        json: dict[str, Any] | None,
    ) -> tuple[int, bytes]:
        """Подписывает запрос, отправляет его и преобразует ошибки соединения."""
        session = self._require_session()
        raw_body = b"" if json is None else orjson.dumps(json)
        headers = build_auth_headers(
            self._config.api_key, self._config.secret, raw_body.decode("utf-8")
        )
        data = None
        if json is not None:
            headers["Content-Type"] = "application/json"
            data = raw_body
        try:
            async with session.request(
                method, path, params=params, data=data, headers=headers
            ) as response:
                return response.status, await response.read()
        except aiohttp.ClientError as error:
            logger.error("Ошибка соединения с API DesslyHub: %s", error)
            raise DesslyHubConnectionError(str(error)) from error

    def _require_session(self) -> aiohttp.ClientSession:
        """Возвращает активную сессию или бросает ошибку, если она не открыта."""
        if self._session is None:
            raise DesslyHubConnectionError("HTTP-сессия DesslyHub не инициализирована")
        return self._session

    def _decode(self, raw: bytes) -> dict[str, Any]:
        """Разбирает тело ответа в словарь, проверяя корректность JSON."""
        try:
            data = orjson.loads(raw)
        except orjson.JSONDecodeError as error:
            logger.error("Не удалось разобрать ответ API DesslyHub: %s", error)
            raise DesslyHubResponseError("Некорректный JSON в ответе API") from error
        if not isinstance(data, dict):
            logger.error("Ответ API DesslyHub не является JSON-объектом")
            raise DesslyHubResponseError("Ожидался JSON-объект в ответе API")
        return data
