from collections.abc import Awaitable, Callable
from decimal import Decimal

import pytest
from aioresponses import aioresponses

from desslyhub_api.client import DesslyHubClient
from desslyhub_api.errors.exceptions import DesslyHubAPIError
from desslyhub_api.models.orders import (
    CreateOrderResponse,
    VoucherServiceResult,
)

BASE_URL = "https://desslyhub.com"


async def test_merchant_get_balance(client: DesslyHubClient, mock_api: aioresponses) -> None:
    """get_balance возвращает баланс с денежными полями типа Decimal."""
    mock_api.get(
        f"{BASE_URL}/api/v1/balance",
        payload={
            "balance": "10.0000",
            "available_balance": "9.0000",
            "overdraft": "0.0000",
            "reserve": "1.0000",
        },
    )

    balance = await client.merchant.get_balance()

    assert balance.balance == Decimal("10.0000")
    assert balance.available_balance == Decimal("9.0000")


async def test_steam_get_games(client: DesslyHubClient, mock_api: aioresponses) -> None:
    """get_games возвращает список игр Steam с app_id и названием."""
    mock_api.get(
        f"{BASE_URL}/api/v1/catalog/steam-gift/games",
        payload={"games": [{"app_id": 730, "name": "CS2"}]},
    )

    games = await client.steam.get_games()

    assert games[0].app_id == 730
    assert games[0].name == "CS2"


async def test_steam_get_editions(client: DesslyHubClient, mock_api: aioresponses) -> None:
    """get_editions возвращает издания игры с ценами по регионам."""
    mock_api.get(
        f"{BASE_URL}/api/v1/catalog/steam-gift/games/730",
        payload={
            "game": [
                {
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
            ]
        },
    )

    editions = await client.steam.get_editions(730)

    assert editions[0].package_id == 1
    assert editions[0].regions_info[0].price == Decimal("1.0000")


async def test_steam_check_login(client: DesslyHubClient, mock_api: aioresponses) -> None:
    """check_login возвращает булев признак возможности пополнения."""
    mock_api.get(
        f"{BASE_URL}/api/v1/catalog/steam-refill/check_login/steam_user",
        payload={"can_refill": True},
    )

    can_refill = await client.steam.check_login("steam_user")

    assert can_refill is True


async def test_mobile_get_games(client: DesslyHubClient, mock_api: aioresponses) -> None:
    """get_games возвращает список мобильных игр."""
    mock_api.get(
        f"{BASE_URL}/api/v1/catalog/mobile-refill/games",
        payload={"games": [{"id": 14, "name": "PUBG"}]},
    )

    games = await client.mobile.get_games()

    assert games[0].id == 14


async def test_mobile_get_game(client: DesslyHubClient, mock_api: aioresponses) -> None:
    """get_game возвращает детали игры с позициями и полями."""
    mock_api.get(
        f"{BASE_URL}/api/v1/catalog/mobile-refill/games/14",
        payload={
            "id": 14,
            "name": "PUBG",
            "positions": [{"id": 22, "name": "60 UC", "price": "1.0000"}],
            "fields": {"Player ID": "Player ID"},
            "servers": {},
        },
    )

    details = await client.mobile.get_game(14)

    assert details.positions[0].price == Decimal("1.0000")
    assert details.fields == {"Player ID": "Player ID"}


async def test_vouchers_get_products(client: DesslyHubClient, mock_api: aioresponses) -> None:
    """get_products возвращает список товаров-ваучеров с вариациями."""
    mock_api.get(
        f"{BASE_URL}/api/v1/catalog/vouchers",
        payload={
            "products": [
                {
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
            ]
        },
    )

    products = await client.vouchers.get_products()

    assert products[0].variations[0].price == Decimal("10.0000")


async def test_vouchers_get_product(client: DesslyHubClient, mock_api: aioresponses) -> None:
    """get_product возвращает один товар-ваучер по идентификатору."""
    mock_api.get(
        f"{BASE_URL}/api/v1/catalog/vouchers/1",
        payload={"id": 1, "name": "V", "country": "US", "variations": []},
    )

    product = await client.vouchers.get_product(1)

    assert product.id == 1
    assert product.variations == []


async def test_esim_get_products(client: DesslyHubClient, mock_api: aioresponses) -> None:
    """get_products возвращает страницу вариантов eSIM с курсорами."""
    mock_api.get(
        f"{BASE_URL}/api/v1/catalog/esim/products",
        payload={
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
        },
    )

    page = await client.esim.get_products()

    assert page.next_cursor == "n"
    assert page.variants[0].attributes.esim_package_type == "data"


async def test_esim_get_product(client: DesslyHubClient, mock_api: aioresponses) -> None:
    """get_product извлекает детали варианта eSIM из поля data."""
    mock_api.get(
        f"{BASE_URL}/api/v1/catalog/esim/products/v1",
        payload={
            "success": True,
            "data": {
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
            },
        },
    )

    details = await client.esim.get_product("v1")

    assert details.id == "v1"
    assert details.products[0].price == 5.0


async def test_exchange_get_all_rates(client: DesslyHubClient, mock_api: aioresponses) -> None:
    """get_all_rates возвращает курсы валют как словарь код->курс."""
    mock_api.get(
        f"{BASE_URL}/api/v1/currency/exchange_rates/steam",
        payload={"exchange_rates": {"1": 1, "2": 0.7425}},
    )

    rates = await client.exchange.get_all_rates()

    assert rates.rates == {1: 1.0, 2: 0.7425}


async def test_exchange_get_rate(client: DesslyHubClient, mock_api: aioresponses) -> None:
    """get_rate возвращает курс конкретной валюты."""
    mock_api.get(
        f"{BASE_URL}/api/v1/currency/exchange_rates/steam/5",
        payload={"exchange_rate": 87.87},
    )

    rate = await client.exchange.get_rate(5)

    assert rate.rate == 87.87


@pytest.mark.parametrize(
    "create_order",
    [
        lambda c: c.orders.create_steam_refill("user", 10.0),
        lambda c: c.orders.create_steam_gift("url", "123", "RU"),
        lambda c: c.orders.create_voucher(1, 2, 1),
        lambda c: c.orders.create_mobile_refill(3, {"player_id": "1"}),
        lambda c: c.orders.create_esim("p", "v"),
    ],
)
async def test_orders_create_methods(
    client: DesslyHubClient,
    mock_api: aioresponses,
    create_order: Callable[[DesslyHubClient], Awaitable[CreateOrderResponse]],
) -> None:
    """Каждый метод создания заказа отправляет POST /orders и возвращает order_id."""
    mock_api.post(
        f"{BASE_URL}/api/v1/orders",
        payload={"order_id": 123, "status": "pending"},
    )

    order = await create_order(client)

    assert order.order_id == 123
    assert order.status == "pending"


async def test_orders_get_with_service_result(
    client: DesslyHubClient, mock_api: aioresponses
) -> None:
    """get разбирает заказ и определяет конкретный тип service_result."""
    mock_api.get(
        f"{BASE_URL}/api/v1/orders/1",
        payload={
            "order_id": 1,
            "order_status": "success",
            "service_type": "voucher",
            "payment_method": "balance",
            "commission": "0.10",
            "final_amount": "1.10",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
            "service_result": {"vouchers": [{"pin": "p", "serialNumber": "s", "expiration": "e"}]},
        },
    )

    order = await client.orders.get(1)

    assert order.commission == Decimal("0.10")
    assert isinstance(order.service_result, VoucherServiceResult)
    assert order.service_result.vouchers[0].serial_number == "s"


async def test_orders_list(client: DesslyHubClient, mock_api: aioresponses) -> None:
    """list возвращает страницу заказов с метаданными пагинации."""
    mock_api.get(
        f"{BASE_URL}/api/v1/orders?limit=20&offset=0",
        payload={
            "items": [
                {
                    "order_id": 1,
                    "order_status": "success",
                    "service_type": "voucher",
                    "payment_method": "balance",
                    "commission": "0.10",
                    "final_amount": "1.10",
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                }
            ],
            "total": 1,
            "limit": 20,
            "offset": 0,
        },
    )

    page = await client.orders.list(limit=20, offset=0)

    assert page.total == 1
    assert page.items[0].order_id == 1


async def test_resource_propagates_api_error(
    client: DesslyHubClient, mock_api: aioresponses
) -> None:
    """Ошибка API 4xx пробрасывается через метод ресурса как DesslyHubAPIError."""
    mock_api.get(
        f"{BASE_URL}/api/v1/balance",
        status=402,
        payload={"error_code": -2, "detail": "Недостаточно средств", "status": 402},
    )

    with pytest.raises(DesslyHubAPIError) as info:
        await client.merchant.get_balance()

    assert info.value.error_code == -2


async def test_client_context_manager(mock_api: aioresponses) -> None:
    """Клиент как контекстный менеджер открывает и закрывает сессию."""
    mock_api.get(
        f"{BASE_URL}/api/v1/balance",
        payload={
            "balance": "1.0000",
            "available_balance": "1.0000",
            "overdraft": "0.0000",
            "reserve": "0.0000",
        },
    )

    async with DesslyHubClient("test-key", "test-secret", base_url=BASE_URL) as instance:
        balance = await instance.merchant.get_balance()

    assert balance.balance == Decimal("1.0000")
