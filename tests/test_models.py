from decimal import Decimal
from typing import Any

import pytest

from desslyhub_api.models.balance import Balance
from desslyhub_api.models.esim import (
    EsimProductDetails,
    EsimProductList,
    EsimProductVariant,
    EsimVariant,
    VariantAttributes,
)
from desslyhub_api.models.exchange import ExchangeRate, ExchangeRates
from desslyhub_api.models.mobile import (
    MobileGame,
    MobileGameDetails,
    MobilePosition,
)
from desslyhub_api.models.orders import (
    CreateOrderResponse,
    EsimServiceResult,
    MobileRefillServiceResult,
    OrderDetails,
    OrderList,
    SteamGiftServiceResult,
    SteamRefillServiceResult,
    VoucherServiceResult,
    VoucherServiceResultItem,
)
from desslyhub_api.models.steam import (
    SteamGiftEdition,
    SteamGiftGame,
    SteamGiftRegionInfo,
)
from desslyhub_api.models.vouchers import VoucherProduct, VoucherVariation


def test_balance_parses_decimal_fields() -> None:
    """Поля баланса разбираются как Decimal с точными значениями."""
    payload: dict[str, Any] = {
        "balance": "10.0000",
        "available_balance": "9.0000",
        "overdraft": "0.0000",
        "reserve": "1.0000",
    }

    model = Balance.model_validate(payload)

    assert model.balance == Decimal("10.0000")
    assert model.available_balance == Decimal("9.0000")
    assert model.overdraft == Decimal("0.0000")
    assert model.reserve == Decimal("1.0000")


def test_exchange_rate_uses_alias() -> None:
    """ExchangeRate читает курс из алиаса exchange_rate."""
    payload: dict[str, Any] = {"exchange_rate": 87.87}

    model = ExchangeRate.model_validate(payload)

    assert model.rate == 87.87


def test_exchange_rates_uses_alias_and_int_keys() -> None:
    """ExchangeRates читает словарь из алиаса exchange_rates с целочисленными ключами."""
    payload: dict[str, Any] = {"exchange_rates": {"1": 1, "2": 0.7425}}

    model = ExchangeRates.model_validate(payload)

    assert model.rates == {1: 1.0, 2: 0.7425}


def test_steam_gift_game_parses() -> None:
    """SteamGiftGame разбирает идентификатор приложения и имя."""
    payload: dict[str, Any] = {"app_id": 730, "name": "CS2"}

    model = SteamGiftGame.model_validate(payload)

    assert model.app_id == 730
    assert model.name == "CS2"


def test_steam_gift_edition_parses_decimal_prices() -> None:
    """SteamGiftEdition разбирает регионы с ценами Decimal."""
    payload: dict[str, Any] = {
        "edition": "Std",
        "package_id": 1,
        "regions_info": [
            {
                "region": "US",
                "discount": "0",
                "price": "1.0000",
                "price_original": "1.0000",
            }
        ],
    }

    model = SteamGiftEdition.model_validate(payload)

    assert model.package_id == 1
    assert isinstance(model.regions_info[0], SteamGiftRegionInfo)
    assert model.regions_info[0].price == Decimal("1.0000")
    assert model.regions_info[0].price_original == Decimal("1.0000")


def test_mobile_game_details_parses() -> None:
    """MobileGameDetails разбирает позиции с Decimal-ценой и словари полей."""
    payload: dict[str, Any] = {
        "id": 14,
        "name": "PUBG",
        "positions": [{"id": 22, "name": "60 UC", "price": "1.0000"}],
        "fields": {"Player ID": "Player ID"},
        "servers": {},
    }

    model = MobileGameDetails.model_validate(payload)

    assert isinstance(model.positions[0], MobilePosition)
    assert model.positions[0].price == Decimal("1.0000")
    assert model.fields == {"Player ID": "Player ID"}
    assert model.servers == {}


def test_mobile_game_parses() -> None:
    """MobileGame разбирает идентификатор и имя игры."""
    payload: dict[str, Any] = {"id": 14, "name": "PUBG"}

    model = MobileGame.model_validate(payload)

    assert model.id == 14
    assert model.name == "PUBG"


def test_voucher_product_parses_decimal_price() -> None:
    """VoucherProduct разбирает вариации с Decimal-ценой и остатком."""
    payload: dict[str, Any] = {
        "id": 1,
        "name": "V",
        "country": "US",
        "variations": [
            {
                "id": 2,
                "name": "10",
                "voucher_currency": "USD",
                "price": "10.0000",
                "stock": 5,
                "benefits": "x",
            }
        ],
    }

    model = VoucherProduct.model_validate(payload)

    assert isinstance(model.variations[0], VoucherVariation)
    assert model.variations[0].price == Decimal("10.0000")
    assert model.variations[0].stock == 5


def test_esim_product_list_parses() -> None:
    """EsimProductList разбирает варианты, атрибуты и курсоры пагинации."""
    payload: dict[str, Any] = {
        "variants": [
            {
                "id": "v1",
                "name": "eSIM",
                "description": "d",
                "image": "img",
                "attributes": {
                    "esim_package_type": "data",
                    "geo_scope": "local",
                    "country": "US",
                    "continent": "NA",
                    "esim_countries": ["US"],
                },
            }
        ],
        "next_cursor": "n",
        "prev_cursor": "p",
    }

    model = EsimProductList.model_validate(payload)

    assert isinstance(model.variants[0], EsimVariant)
    assert isinstance(model.variants[0].attributes, VariantAttributes)
    assert model.next_cursor == "n"
    assert model.prev_cursor == "p"


def test_esim_product_details_parses() -> None:
    """EsimProductDetails разбирает продукты с ценой и лимитами заказа."""
    payload: dict[str, Any] = {
        "id": "v1",
        "name": "eSIM",
        "description": "d",
        "image": "img",
        "attributes": {"esim_package_type": "data", "geo_scope": "local"},
        "products": [
            {
                "id": "p1",
                "name": "1GB",
                "description": "d",
                "price": 5.0,
                "stock": 10,
                "max_per_order": 2,
                "attributes": {},
            }
        ],
    }

    model = EsimProductDetails.model_validate(payload)

    assert isinstance(model.products[0], EsimProductVariant)
    assert model.products[0].price == 5.0
    assert model.products[0].max_per_order == 2


def test_create_order_response_parses() -> None:
    """CreateOrderResponse разбирает идентификатор и статус заказа."""
    payload: dict[str, Any] = {"order_id": 123, "status": "pending"}

    model = CreateOrderResponse.model_validate(payload)

    assert model.order_id == 123
    assert model.status == "pending"


def test_voucher_service_result_item_uses_serial_number_alias() -> None:
    """VoucherServiceResultItem читает серийный номер из алиаса serialNumber."""
    payload: dict[str, Any] = {"pin": "p", "serialNumber": "s", "expiration": "e"}

    model = VoucherServiceResultItem.model_validate(payload)

    assert model.pin == "p"
    assert model.serial_number == "s"
    assert model.expiration == "e"


def _order_payload(service_result: dict[str, Any]) -> dict[str, Any]:
    """Собирает тело заказа с заданным результатом сервиса."""
    return {
        "order_id": 1,
        "order_status": "success",
        "service_type": "voucher",
        "payment_method": "balance",
        "commission": "0.10",
        "final_amount": "1.10",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "completed_at": "2025-01-01T00:00:00Z",
        "error_code": "",
        "payment_url": "",
        "service_result": service_result,
    }


def test_order_details_parses_decimal_fields() -> None:
    """OrderDetails разбирает комиссию и итоговую сумму как Decimal."""
    payload = _order_payload({"vouchers": [{"pin": "p", "serialNumber": "s", "expiration": "e"}]})

    model = OrderDetails.model_validate(payload)

    assert model.commission == Decimal("0.10")
    assert model.final_amount == Decimal("1.10")


@pytest.mark.parametrize(
    ("service_result", "expected_type"),
    [
        (
            {"vouchers": [{"pin": "p", "serialNumber": "s", "expiration": "e"}]},
            VoucherServiceResult,
        ),
        ({"pkg_id": "1", "region": "US"}, SteamGiftServiceResult),
        ({"amount": 1.0, "username": "u"}, SteamRefillServiceResult),
        ({"position": 1, "fields": {"a": "b"}}, MobileRefillServiceResult),
        (
            {
                "iccid": "i",
                "matching_id": "m",
                "qr_code_text": "q",
                "smdp_address": "s",
                "status": "active",
                "created_at": "t",
            },
            EsimServiceResult,
        ),
    ],
)
def test_order_details_service_result_union(
    service_result: dict[str, Any], expected_type: type[Any]
) -> None:
    """Union service_result разбирается в корректный подтип модели результата."""
    payload = _order_payload(service_result)

    model = OrderDetails.model_validate(payload)

    assert isinstance(model.service_result, expected_type)


def test_order_list_parses() -> None:
    """OrderList разбирает список заказов и параметры пагинации."""
    order = _order_payload({"vouchers": []})
    payload: dict[str, Any] = {"items": [order], "total": 1, "limit": 20, "offset": 0}

    model = OrderList.model_validate(payload)

    assert isinstance(model.items[0], OrderDetails)
    assert model.total == 1
    assert model.limit == 20
    assert model.offset == 0
