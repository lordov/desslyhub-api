from desslyhub_api.http.transport import HttpTransport
from desslyhub_api.models.esim import EsimProductDetails, EsimProductList


class EsimResource:
    """Операции каталога eSIM: список вариантов и вариант по идентификатору."""

    def __init__(self, transport: HttpTransport) -> None:
        """Сохраняет транспорт для выполнения запросов к API."""
        self._transport = transport

    async def get_products(self, cursor: str | None = None) -> EsimProductList:
        """Возвращает страницу списка вариантов eSIM с курсорной пагинацией."""
        params = {"cursor": cursor} if cursor is not None else None
        payload = await self._transport.request(
            "GET", "/api/v1/catalog/esim/products", params=params
        )
        return EsimProductList.model_validate(payload)

    async def get_product(self, variant_id: str) -> EsimProductDetails:
        """Возвращает подробную информацию о варианте eSIM по идентификатору."""
        payload = await self._transport.request(
            "GET", f"/api/v1/catalog/esim/products/{variant_id}"
        )
        return EsimProductDetails.model_validate(payload["data"])
