from desslyhub_api.http.transport import HttpTransport
from desslyhub_api.models.vouchers import VoucherProduct


class VouchersResource:
    """Операции каталога ваучеров: список товаров и товар по идентификатору."""

    def __init__(self, transport: HttpTransport) -> None:
        """Сохраняет транспорт для выполнения запросов к API."""
        self._transport = transport

    async def get_products(self) -> list[VoucherProduct]:
        """Возвращает список доступных товаров-ваучеров."""
        payload = await self._transport.request("GET", "/api/v1/catalog/vouchers")
        return [VoucherProduct.model_validate(item) for item in payload["products"]]

    async def get_product(self, product_id: int) -> VoucherProduct:
        """Возвращает товар-ваучер по его идентификатору."""
        payload = await self._transport.request("GET", f"/api/v1/catalog/vouchers/{product_id}")
        return VoucherProduct.model_validate(payload)
