from typing import Any

ERROR_MESSAGES: dict[int, str] = {
    -1: "Внутренняя ошибка сервера",
    -2: "Недостаточно средств на балансе",
    -3: "Некорректная сумма",
    -4: "Некорректное тело запроса",
    -5: "Доступ запрещён",
    -51: "Некорректная ссылка для добавления в друзья",
    -52: "Некорректный app ID",
    -53: "Информация об игре не найдена",
    -54: "У пользователя нет основной игры",
    -55: "У пользователя уже есть эта игра",
    -56: "Не удалось добавить в друзья",
    -57: "Указан некорректный регион покупателя",
    -58: "Регион получателя недоступен для подарка",
    -59: "Пользователь не добавил/не удалил бота из списка друзей",
    -100: "Некорректное имя пользователя Steam",
    -120: "Некорректное значение валюты",
    -121: "Валюта не поддерживается",
    -151: "Некорректный ID транзакции",
    -152: "Транзакция не найдена",
    -153: "Не указан номер страницы",
    -200: "Мобильная игра не найдена",
    -201: "Позиция мобильной игры не найдена",
    -202: "Исходный вариант не найден",
    -300: "Ваучер не найден",
    -301: "Ваучер недоступен",
}


class DesslyHubError(Exception):
    """Базовое исключение библиотеки DesslyHub."""


class DesslyHubConnectionError(DesslyHubError):
    """Ошибка сетевого соединения с API DesslyHub."""


class DesslyHubResponseError(DesslyHubError):
    """Ошибка разбора некорректного ответа API DesslyHub."""


class DesslyHubAPIError(DesslyHubError):
    """Ошибка, возвращённая API DesslyHub с ненулевым HTTP-статусом."""

    def __init__(
        self,
        error_code: int,
        message: str,
        http_status: int | None = None,
    ) -> None:
        """Сохраняет код ошибки API, текст и HTTP-статус ответа."""
        self.error_code = error_code
        self.message = message
        self.http_status = http_status
        super().__init__(f"[{error_code}] {message}")


def raise_from_error_model(http_status: int, payload: dict[str, Any]) -> None:
    """Бросает DesslyHubAPIError на основе тела ошибки ErrorModel."""
    error_code = int(payload.get("error_code", 0) or 0)
    message = (
        payload.get("detail")
        or payload.get("title")
        or ERROR_MESSAGES.get(error_code)
        or "Неизвестная ошибка API"
    )
    raise DesslyHubAPIError(error_code, str(message), http_status=http_status)
