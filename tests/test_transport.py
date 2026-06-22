from typing import Any

import aiohttp
import pytest
from aioresponses import aioresponses

from desslyhub_api.config.settings import ClientConfig
from desslyhub_api.errors.exceptions import (
    DesslyHubAPIError,
    DesslyHubConnectionError,
    DesslyHubResponseError,
)
from desslyhub_api.http.transport import HttpTransport

BASE_URL = "https://desslyhub.com"


def _transport() -> HttpTransport:
    """Создаёт транспорт с тестовой конфигурацией."""
    return HttpTransport(ClientConfig("test-key", "test-secret", base_url=BASE_URL))


async def test_request_parses_success_payload(mock_api: aioresponses) -> None:
    """Успешный ответ 2xx разбирается и возвращается как словарь."""
    mock_api.get(f"{BASE_URL}/api/v1/balance", status=200, payload={"ok": True})

    transport = _transport()
    await transport.start()
    try:
        result = await transport.request("GET", "/api/v1/balance")
    finally:
        await transport.close()

    assert result == {"ok": True}


async def test_request_raises_api_error_on_4xx(mock_api: aioresponses) -> None:
    """Ответ 4xx с телом ErrorModel приводит к DesslyHubAPIError с верным кодом."""
    mock_api.get(
        f"{BASE_URL}/api/v1/balance",
        status=400,
        payload={
            "error_code": -2,
            "title": "Payment Required",
            "detail": "Недостаточно средств",
            "status": 400,
        },
    )

    transport = _transport()
    await transport.start()
    try:
        with pytest.raises(DesslyHubAPIError) as info:
            await transport.request("GET", "/api/v1/balance")
    finally:
        await transport.close()

    assert info.value.error_code == -2
    assert info.value.http_status == 400


async def test_request_raises_connection_error(mock_api: aioresponses) -> None:
    """Сетевая ошибка aiohttp преобразуется в DesslyHubConnectionError."""
    mock_api.get(
        f"{BASE_URL}/api/v1/balance",
        exception=aiohttp.ClientConnectionError("boom"),
    )

    transport = _transport()
    await transport.start()
    try:
        with pytest.raises(DesslyHubConnectionError):
            await transport.request("GET", "/api/v1/balance")
    finally:
        await transport.close()


@pytest.mark.parametrize(
    "body",
    [b"not-json", b"[1, 2, 3]"],
)
async def test_request_raises_response_error_on_bad_json(
    mock_api: aioresponses, body: bytes
) -> None:
    """Некорректный или не-объектный JSON приводит к DesslyHubResponseError."""
    mock_api.get(f"{BASE_URL}/api/v1/balance", status=200, body=body)

    transport = _transport()
    await transport.start()
    try:
        with pytest.raises(DesslyHubResponseError):
            await transport.request("GET", "/api/v1/balance")
    finally:
        await transport.close()


async def test_request_without_session_raises_connection_error() -> None:
    """Запрос без открытой сессии приводит к DesslyHubConnectionError."""
    transport = _transport()

    with pytest.raises(DesslyHubConnectionError):
        await transport.request("GET", "/api/v1/balance")


async def test_transport_context_manager(mock_api: aioresponses) -> None:
    """Контекстный менеджер транспорта открывает и закрывает сессию."""
    mock_api.get(f"{BASE_URL}/api/v1/balance", status=200, payload={"ok": True})

    async with _transport() as transport:
        result = await transport.request("GET", "/api/v1/balance")

    assert result == {"ok": True}


async def test_request_sends_json_body(mock_api: aioresponses) -> None:
    """POST-запрос с телом JSON выполняется и возвращает разобранный ответ."""
    mock_api.post(f"{BASE_URL}/api/v1/orders", status=200, payload={"order_id": 1})

    transport = _transport()
    await transport.start()
    try:
        result: dict[str, Any] = await transport.request("POST", "/api/v1/orders", json={"a": "b"})
    finally:
        await transport.close()

    assert result == {"order_id": 1}
