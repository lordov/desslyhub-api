from types import TracebackType

from desslyhub_api.config.settings import (
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT_SECONDS,
    ClientConfig,
)
from desslyhub_api.http.transport import HttpTransport
from desslyhub_api.resources.esim import EsimResource
from desslyhub_api.resources.exchange import ExchangeResource
from desslyhub_api.resources.merchant import MerchantResource
from desslyhub_api.resources.mobile import MobileResource
from desslyhub_api.resources.orders import OrdersResource
from desslyhub_api.resources.steam import SteamResource
from desslyhub_api.resources.vouchers import VouchersResource


class DesslyHubClient:
    """Асинхронный клиент DesslyHub с доступом ко всем группам операций API."""

    def __init__(
        self,
        api_key: str,
        secret: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        """Создаёт транспорт и инициализирует ресурсы для групп эндпоинтов."""
        self._transport = HttpTransport(
            ClientConfig(
                api_key=api_key,
                secret=secret,
                base_url=base_url,
                timeout_seconds=timeout_seconds,
            )
        )
        self.steam = SteamResource(self._transport)
        self.mobile = MobileResource(self._transport)
        self.vouchers = VouchersResource(self._transport)
        self.esim = EsimResource(self._transport)
        self.orders = OrdersResource(self._transport)
        self.merchant = MerchantResource(self._transport)
        self.exchange = ExchangeResource(self._transport)

    async def __aenter__(self) -> "DesslyHubClient":
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
        """Открывает постоянную HTTP-сессию для повторного использования."""
        await self._transport.start()

    async def close(self) -> None:
        """Закрывает HTTP-сессию клиента."""
        await self._transport.close()
