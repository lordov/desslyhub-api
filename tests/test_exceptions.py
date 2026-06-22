from typing import Any

import pytest

from desslyhub_api.errors.exceptions import (
    DesslyHubAPIError,
    DesslyHubConnectionError,
    DesslyHubError,
    DesslyHubResponseError,
    raise_from_error_model,
)


def test_api_error_stores_attributes() -> None:
    """DesslyHubAPIError сохраняет код ошибки, текст и HTTP-статус."""
    error = DesslyHubAPIError(-2, "Недостаточно средств", http_status=400)

    assert error.error_code == -2
    assert error.message == "Недостаточно средств"
    assert error.http_status == 400
    assert str(error) == "[-2] Недостаточно средств"


@pytest.mark.parametrize(
    "exc_type",
    [DesslyHubConnectionError, DesslyHubResponseError, DesslyHubAPIError],
)
def test_exceptions_inherit_base(exc_type: type[DesslyHubError]) -> None:
    """Все специализированные исключения наследуются от базового DesslyHubError."""
    is_subclass = issubclass(exc_type, DesslyHubError)

    assert is_subclass


def test_raise_from_error_model_prefers_detail() -> None:
    """Сообщение берётся из поля detail тела ошибки."""
    payload: dict[str, Any] = {
        "error_code": -2,
        "title": "Payment Required",
        "detail": "Недостаточно средств",
        "status": 400,
    }

    with pytest.raises(DesslyHubAPIError) as info:
        raise_from_error_model(400, payload)

    assert info.value.error_code == -2
    assert info.value.message == "Недостаточно средств"
    assert info.value.http_status == 400


def test_raise_from_error_model_falls_back_to_title() -> None:
    """При отсутствии detail сообщение берётся из title."""
    payload: dict[str, Any] = {"error_code": -5, "title": "Forbidden", "status": 403}

    with pytest.raises(DesslyHubAPIError) as info:
        raise_from_error_model(403, payload)

    assert info.value.message == "Forbidden"


def test_raise_from_error_model_known_code_message() -> None:
    """Для известного кода без текста используется встроенное сообщение."""
    payload: dict[str, Any] = {"error_code": -300}

    with pytest.raises(DesslyHubAPIError) as info:
        raise_from_error_model(404, payload)

    assert info.value.error_code == -300
    assert info.value.message == "Ваучер не найден"


def test_raise_from_error_model_unknown_code_message() -> None:
    """Для неизвестного кода без текста используется сообщение по умолчанию."""
    payload: dict[str, Any] = {"error_code": -9999}

    with pytest.raises(DesslyHubAPIError) as info:
        raise_from_error_model(500, payload)

    assert info.value.error_code == -9999
    assert info.value.message == "Неизвестная ошибка API"
