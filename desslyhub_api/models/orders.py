from decimal import Decimal
from typing import Any, Union

from pydantic import Field

from desslyhub_api.models.base import DesslyHubModel


class PaylinkQRPaymentParams(DesslyHubModel):
    """Параметры оплаты заказа по QR-ссылке."""

    amount: int
    success_url: str
    fail_url: str


class SteamRefillServiceResult(DesslyHubModel):
    """Результат заказа пополнения Steam."""

    amount: float
    username: str


class SteamGiftServiceResult(DesslyHubModel):
    """Результат заказа подарка Steam."""

    pkg_id: str
    region: str
    bot_id: str = ""
    invite_url: str = ""
    steam_id: str = ""


class VoucherServiceResultItem(DesslyHubModel):
    """Один выданный код ваучера."""

    pin: str
    serial_number: str = Field(default="", alias="serialNumber")
    expiration: str = ""


class VoucherServiceResult(DesslyHubModel):
    """Результат заказа ваучеров с выданными кодами."""

    vouchers: list[VoucherServiceResultItem]


class MobileRefillServiceResult(DesslyHubModel):
    """Результат заказа пополнения мобильной игры."""

    position: int
    fields: dict[str, Any]


class EsimServiceResult(DesslyHubModel):
    """Результат заказа eSIM с данными для активации."""

    iccid: str
    matching_id: str
    qr_code_text: str
    smdp_address: str
    status: str
    created_at: str
    can_renew: bool = False
    last_bundle: str = ""
    android_universal_link: str = ""
    universal_link: str = ""


ServiceResult = Union[
    SteamRefillServiceResult,
    SteamGiftServiceResult,
    VoucherServiceResult,
    MobileRefillServiceResult,
    EsimServiceResult,
]


class CreateOrderResponse(DesslyHubModel):
    """Ответ на создание заказа: идентификатор и статус."""

    order_id: int
    status: str


class OrderDetails(DesslyHubModel):
    """Подробные сведения о заказе и результате его выполнения."""

    order_id: int
    order_status: str
    service_type: str
    payment_method: str
    commission: Decimal
    final_amount: Decimal
    created_at: str
    updated_at: str
    completed_at: str | None = None
    error_code: str = ""
    payment_url: str = ""
    service_result: ServiceResult | None = None


class OrderList(DesslyHubModel):
    """Страница списка заказов с общим количеством записей."""

    items: list[OrderDetails]
    total: int
    limit: int
    offset: int
