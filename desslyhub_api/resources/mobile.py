from desslyhub_api.http.transport import HttpTransport
from desslyhub_api.models.mobile import MobileGame, MobileGameDetails


class MobileResource:
    """Операции каталога мобильных игр: список и подробная информация об игре."""

    def __init__(self, transport: HttpTransport) -> None:
        """Сохраняет транспорт для выполнения запросов к API."""
        self._transport = transport

    async def get_games(self) -> list[MobileGame]:
        """Возвращает список мобильных игр, доступных для пополнения."""
        payload = await self._transport.request("GET", "/api/v1/catalog/mobile-refill/games")
        return [MobileGame.model_validate(item) for item in payload["games"]]

    async def get_game(self, game_id: int) -> MobileGameDetails:
        """Возвращает подробную информацию о мобильной игре по идентификатору."""
        payload = await self._transport.request(
            "GET", f"/api/v1/catalog/mobile-refill/games/{game_id}"
        )
        return MobileGameDetails.model_validate(payload)
