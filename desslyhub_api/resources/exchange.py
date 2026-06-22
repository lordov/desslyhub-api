from desslyhub_api.enums.currency import Currency
from desslyhub_api.http.transport import HttpTransport
from desslyhub_api.models.exchange import ExchangeRate, ExchangeRates


class ExchangeResource:
    """Операции с курсами валют: все курсы и курс по коду валюты."""

    def __init__(self, transport: HttpTransport) -> None:
        """Сохраняет транспорт для выполнения запросов к API."""
        self._transport = transport

    async def get_all_rates(self) -> ExchangeRates:
        """Возвращает курсы всех поддерживаемых валют к доллару США."""
        payload = await self._transport.request("GET", "/api/v1/currency/exchange_rates/steam")
        return ExchangeRates.model_validate(payload)

    async def get_rate(self, currency: Currency | int) -> ExchangeRate:
        """Возвращает курс указанной валюты к доллару США."""
        payload = await self._transport.request(
            "GET", f"/api/v1/currency/exchange_rates/steam/{int(currency)}"
        )
        return ExchangeRate.model_validate(payload)
