from desslyhub_api.http.transport import HttpTransport
from desslyhub_api.models.steam import SteamGiftEdition, SteamGiftGame


class SteamResource:
    """Операции каталога Steam: список игр, издания и проверка логина для пополнения."""

    def __init__(self, transport: HttpTransport) -> None:
        """Сохраняет транспорт для выполнения запросов к API."""
        self._transport = transport

    async def get_games(self) -> list[SteamGiftGame]:
        """Возвращает список игр Steam, доступных для подарка."""
        payload = await self._transport.request("GET", "/api/v1/catalog/steam-gift/games")
        return [SteamGiftGame.model_validate(item) for item in payload["games"]]

    async def get_editions(self, app_id: int) -> list[SteamGiftEdition]:
        """Возвращает издания игры Steam по её app_id."""
        payload = await self._transport.request("GET", f"/api/v1/catalog/steam-gift/games/{app_id}")
        return [SteamGiftEdition.model_validate(item) for item in payload["game"]]

    async def check_login(self, username: str) -> bool:
        """Проверяет, можно ли пополнить аккаунт Steam с указанным логином."""
        payload = await self._transport.request(
            "GET", f"/api/v1/catalog/steam-refill/check_login/{username}"
        )
        return bool(payload["can_refill"])
