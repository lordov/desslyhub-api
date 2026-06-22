from desslyhub_api.http.transport import HttpTransport
from desslyhub_api.models.balance import Balance


class MerchantResource:
    """Операции мерчанта: текущий баланс."""

    def __init__(self, transport: HttpTransport) -> None:
        """Сохраняет транспорт для выполнения запросов к API."""
        self._transport = transport

    async def get_balance(self) -> Balance:
        """Возвращает текущий баланс мерчанта."""
        payload = await self._transport.request("GET", "/api/v1/balance")
        return Balance.model_validate(payload)
