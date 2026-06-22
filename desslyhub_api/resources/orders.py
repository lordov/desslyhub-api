from typing import Any

from desslyhub_api.enums.orders import PaymentMethod, ServiceType
from desslyhub_api.http.transport import HttpTransport
from desslyhub_api.models.orders import (
    CreateOrderResponse,
    OrderDetails,
    OrderList,
    PaylinkQRPaymentParams,
)


class OrdersResource:
    """Операции с заказами: создание по типам сервиса, список и детали заказа."""

    def __init__(self, transport: HttpTransport) -> None:
        """Сохраняет транспорт для выполнения запросов к API."""
        self._transport = transport

    async def create_steam_refill(
        self,
        username: str,
        amount: float,
        *,
        payment_method: PaymentMethod = PaymentMethod.BALANCE,
        payment_params: PaylinkQRPaymentParams | None = None,
        reference: str | None = None,
    ) -> CreateOrderResponse:
        """Создаёт заказ на пополнение аккаунта Steam."""
        return await self._create(
            ServiceType.STEAM_REFILL,
            {"username": username, "amount": amount},
            payment_method,
            payment_params,
            reference,
        )

    async def create_steam_gift(
        self,
        invite_url: str,
        package_id: str,
        region: str,
        *,
        payment_method: PaymentMethod = PaymentMethod.BALANCE,
        payment_params: PaylinkQRPaymentParams | None = None,
        reference: str | None = None,
    ) -> CreateOrderResponse:
        """Создаёт заказ на подарок игры Steam."""
        return await self._create(
            ServiceType.STEAM_GIFT,
            {"invite_url": invite_url, "package_id": package_id, "region": region},
            payment_method,
            payment_params,
            reference,
        )

    async def create_voucher(
        self,
        root_id: int,
        variant_id: int,
        quantity: int,
        *,
        payment_method: PaymentMethod = PaymentMethod.BALANCE,
        payment_params: PaylinkQRPaymentParams | None = None,
        reference: str | None = None,
    ) -> CreateOrderResponse:
        """Создаёт заказ на покупку ваучеров."""
        return await self._create(
            ServiceType.VOUCHER,
            {"root_id": root_id, "variant_id": variant_id, "quantity": quantity},
            payment_method,
            payment_params,
            reference,
        )

    async def create_mobile_refill(
        self,
        position: int,
        fields: dict[str, str],
        *,
        payment_method: PaymentMethod = PaymentMethod.BALANCE,
        payment_params: PaylinkQRPaymentParams | None = None,
        reference: str | None = None,
    ) -> CreateOrderResponse:
        """Создаёт заказ на пополнение мобильной игры."""
        return await self._create(
            ServiceType.MOBILE_REFILL,
            {"position": position, "fields": fields},
            payment_method,
            payment_params,
            reference,
        )

    async def create_esim(
        self,
        product_id: str,
        variant_id: str,
        *,
        payment_method: PaymentMethod = PaymentMethod.BALANCE,
        payment_params: PaylinkQRPaymentParams | None = None,
        reference: str | None = None,
    ) -> CreateOrderResponse:
        """Создаёт заказ на покупку eSIM."""
        return await self._create(
            ServiceType.ESIM,
            {"product_id": product_id, "variant_id": variant_id},
            payment_method,
            payment_params,
            reference,
        )

    async def list(
        self,
        limit: int | None = None,
        offset: int | None = None,
    ) -> OrderList:
        """Возвращает страницу списка заказов с пагинацией limit/offset."""
        params = {}
        if limit is not None:
            params["limit"] = str(limit)
        if offset is not None:
            params["offset"] = str(offset)
        payload = await self._transport.request("GET", "/api/v1/orders", params=params or None)
        return OrderList.model_validate(payload)

    async def get(self, order_id: int) -> OrderDetails:
        """Возвращает подробные сведения о заказе по его идентификатору."""
        payload = await self._transport.request("GET", f"/api/v1/orders/{order_id}")
        return OrderDetails.model_validate(payload)

    async def _create(
        self,
        service_type: ServiceType,
        service_params: dict[str, Any],
        payment_method: PaymentMethod,
        payment_params: PaylinkQRPaymentParams | None,
        reference: str | None,
    ) -> CreateOrderResponse:
        """Формирует тело заказа и отправляет запрос на создание заказа."""
        body: dict[str, Any] = {
            "payment_method": payment_method,
            "service_type": service_type,
            "service_params": service_params,
        }
        if payment_params is not None:
            body["payment_params"] = payment_params.model_dump()
        if reference is not None:
            body["reference"] = reference
        payload = await self._transport.request("POST", "/api/v1/orders", json=body)
        return CreateOrderResponse.model_validate(payload)
