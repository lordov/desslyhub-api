from decimal import Decimal

from desslyhub_api.models.base import DesslyHubModel


class VoucherVariation(DesslyHubModel):
    """Вариация ваучера: цена, валюта, остаток и описание."""

    id: int
    name: str
    voucher_currency: str
    price: Decimal
    stock: int
    benefits: str = ""


class VoucherProduct(DesslyHubModel):
    """Товар-ваучер с доступными вариациями."""

    id: int
    name: str
    country: str = ""
    variations: list[VoucherVariation]
