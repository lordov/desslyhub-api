<p align="center">
  <img src="https://raw.githubusercontent.com/lordov/desslyhub/main/assets/logo.svg" alt="DesslyHub API" width="320">
</p>

<h1 align="center">desslyhub-api</h1>

<p align="center">
  Async Python client for the <a href="https://desslyhub.com/readme/">DesslyHub API</a>:<br>
  Steam, mobile games, vouchers, eSIM, merchant balance, orders and currency exchange rates.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12%2B-3776AB?logo=python&logoColor=white" alt="Python 3.12+">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT">
  <img src="https://img.shields.io/badge/code%20style-black-000000" alt="black">
  <img src="https://img.shields.io/badge/types-mypy-2A6DB2" alt="mypy">
  <img src="https://img.shields.io/badge/async-aiohttp%20%2B%20orjson-FF69B4" alt="aiohttp + orjson">
</p>

<p align="center">
  <b>English</b> · <a href="https://github.com/lordov/desslyhub/blob/main/README.ru.md">Русский</a>
</p>

---

Built on `aiohttp` + `orjson`, responses are validated with `pydantic`, and monetary values are represented as `Decimal`. All endpoints live under the base URL `https://desslyhub.com` with the `/api/v1/` prefix.

## Contents

- [Features](#features)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Authentication](#authentication)
- [Usage](#usage)
- [Orders](#orders)
- [Money values and error handling](#money-values-and-error-handling)
- [Development](#development)
- [License](#license)

## Features

| Resource | Purpose |
| --- | --- |
| `client.steam` | Catalog of gift games, game editions and login check for top-ups. |
| `client.mobile` | Catalog of mobile games and details of a specific game. |
| `client.vouchers` | Catalog of voucher products and a product by id. |
| `client.esim` | Catalog of eSIM variants with cursor pagination and variant details. |
| `client.merchant` | Current merchant balance. |
| `client.exchange` | Currency rates against USD for Steam top-ups. |
| `client.orders` | Single entry point for creating all purchases (top-ups, gifts, vouchers, eSIM), plus listing and order details. |

> All purchases are created through the `orders` resource (single endpoint `POST /api/v1/orders`). The old `gift` / `top_up` / `refill` / `buy` methods and the `merchants` resource with `/transactions` endpoints were removed — order history and statuses are now handled by orders.

## Installation

**Requirements:** Python 3.12+ and [uv](https://docs.astral.sh/uv/).

### For end users

```bash
uv add desslyhub-api
# or
pip install desslyhub-api
```

Import the package: `import desslyhub_api`.

### For local development

Clone the repository and install all dependency groups (including the dev tools: pytest, black, isort, mypy):

```bash
uv sync --all-groups
```

## Quick start

```python
import asyncio

from desslyhub_api import DesslyHubClient


async def main() -> None:
    async with DesslyHubClient("YOUR_API_KEY", "YOUR_SECRET") as client:
        balance = await client.merchant.get_balance()
        print(balance.balance)  # Decimal


asyncio.run(main())
```

The client is an async context manager: inside `async with` it opens a persistent HTTP session that is closed automatically on exit.

## Authentication

Every request is signed with HMAC-SHA256: `signature = HMAC_SHA256(secret, api_key + timestamp + body)`. The client adds the `X-Api-Key`, `X-Timestamp` (Unix time in seconds) and `X-Signature` headers to every request. So you need **two** values — `api_key` and `secret`. The default base URL is `https://desslyhub.com`.

```python
from desslyhub_api import DesslyHubClient

# Minimal
client = DesslyHubClient("YOUR_API_KEY", "YOUR_SECRET")

# Overriding base_url and timeout
client = DesslyHubClient(
    "YOUR_API_KEY",
    "YOUR_SECRET",
    base_url="https://desslyhub.com",
    timeout_seconds=30.0,
)
```

## Usage

All methods are async and called inside `async with DesslyHubClient(api_key, secret) as client:`.

### Merchant balance

```python
balance = await client.merchant.get_balance()
print(balance.balance)            # Decimal — total balance
print(balance.available_balance)  # Decimal — available to spend
print(balance.overdraft)          # Decimal — overdraft limit
print(balance.reserve)            # Decimal — reserved funds
```

`get_balance()` returns a `Balance` model with fields `balance`, `available_balance`, `overdraft`, `reserve` — all of type `Decimal`.

### Steam: games catalog, editions and login check

```python
games = await client.steam.get_games()
for game in games:
    print(game)

# Editions of a specific game by its app_id
editions = await client.steam.get_editions(app_id=730)
for edition in editions:
    print(edition)

# Whether a Steam account with the given login can be topped up
can_refill = await client.steam.check_login(username="steam_user")
print(can_refill)  # bool
```

### Mobile: catalog and game details

```python
games = await client.mobile.get_games()
for game in games:
    print(game)

details = await client.mobile.get_game(game_id=42)
print(details)
```

### Vouchers: catalog

```python
products = await client.vouchers.get_products()
for product in products:
    print(product)

product = await client.vouchers.get_product(product_id=10)
print(product)
```

### eSIM: catalog

```python
page = await client.esim.get_products()  # cursor=None — first page
for variant in page.variants:
    print(variant)

# Next page by cursor
if page.next_cursor:
    next_page = await client.esim.get_products(cursor=page.next_cursor)
    print(next_page.variants)

details = await client.esim.get_product(variant_id="variant-123")
print(details)
```

### Exchange: currency rates

```python
from desslyhub_api import Currency

all_rates = await client.exchange.get_all_rates()
print(all_rates.rates)  # dict[int, float]

# Rate for a specific currency (Currency enum or numeric code)
rate = await client.exchange.get_rate(Currency.RUB)
print(rate.rate)
```

## Orders

All purchases are created through the `client.orders` resource. Each `create_*` method returns `CreateOrderResponse` with fields `order_id` (int) and `status` (str). Typical flow:

1. Create an order with a `create_*` method — the response contains `order_id` and `status`.
2. Poll the order via `client.orders.get(order_id)`, tracking `order_status` and `service_result` (the result becomes available after successful completion).

All `create_*` methods share common keyword-only optional parameters:

- `payment_method: PaymentMethod` — payment method, defaults to `PaymentMethod.BALANCE` (charge the merchant balance). For QR-link payment use `PaymentMethod.PAYLINK_QR`.
- `payment_params: PaylinkQRPaymentParams | None` — QR payment parameters (required for `PAYLINK_QR`).
- `reference: str | None` — your external order id.

### Payment from balance (default)

```python
# Steam top-up
order = await client.orders.create_steam_refill(
    username="steam_user",
    amount=10.0,                 # amount in USD
    reference="my-order-id",     # optional
)
print(order.order_id, order.status)

# Steam game gift
order = await client.orders.create_steam_gift(
    invite_url="https://steamcommunity.com/p/...",
    package_id="12345",
    region="RU",
)

# Voucher purchase
order = await client.orders.create_voucher(
    root_id=10,
    variant_id=2,
    quantity=1,
)

# Mobile game top-up
order = await client.orders.create_mobile_refill(
    position=3,
    fields={"player_id": "123456"},
)

# eSIM purchase
order = await client.orders.create_esim(
    product_id="product-123",
    variant_id="variant-456",
)
```

### Payment via QR link (PAYLINK_QR)

```python
from desslyhub_api import PaymentMethod, PaylinkQRPaymentParams

order = await client.orders.create_steam_refill(
    username="steam_user",
    amount=10.0,
    payment_method=PaymentMethod.PAYLINK_QR,
    payment_params=PaylinkQRPaymentParams(
        amount=1000,
        success_url="https://example.com/success",
        fail_url="https://example.com/fail",
    ),
    reference="my-order-id",
)
print(order.order_id, order.status)
```

### Listing and order details

```python
# List page with limit/offset pagination
page = await client.orders.list(limit=20, offset=0)
print(page.total, page.limit, page.offset)
for item in page.items:
    print(item.order_id, item.order_status)

# Details of a specific order
details = await client.orders.get(order_id=12345)
print(details.order_status)    # str — order status
print(details.service_type)    # str — service type
print(details.commission)      # Decimal — commission
print(details.final_amount)    # Decimal — final amount
print(details.service_result)  # execution result (after success)
```

`list()` returns `OrderList` with fields `items`, `total`, `limit`, `offset`. `get()` returns `OrderDetails` with fields `order_id`, `order_status`, `service_type`, `payment_method`, `commission` and `final_amount` (both `Decimal`), timestamps and `service_result`.

## Money values and error handling

- Monetary values (e.g. `Balance` fields, as well as `commission` and `final_amount` in `OrderDetails`) are represented as `Decimal` to avoid rounding errors.
- On a response HTTP status `>= 400` the client raises `DesslyHubAPIError`. The error body is parsed as RFC 7807 (`ErrorModel`). The exception exposes `error_code` (int), `message` (str) and `http_status` (int | None) attributes.
- Network problems raise `DesslyHubConnectionError`.
- An invalid/unreadable API response raises `DesslyHubResponseError`.
- All exceptions inherit from the base `DesslyHubError`.

```python
from desslyhub_api import (
    DesslyHubAPIError,
    DesslyHubConnectionError,
    DesslyHubResponseError,
)

async with DesslyHubClient(api_key, secret) as client:
    try:
        balance = await client.merchant.get_balance()
    except DesslyHubAPIError as error:
        print("API error:", error.error_code, error.message, error.http_status)
    except DesslyHubConnectionError as error:
        print("Connection error:", error)
    except DesslyHubResponseError as error:
        print("Invalid response:", error)
```

## Development

Set up the environment with all dev dependencies (pytest, black, isort, mypy):

```bash
uv sync --all-groups
```

Useful commands:

```bash
uv run pytest -q                   # tests
uv run isort . && uv run black .   # formatting
uv run mypy desslyhub_api          # type checking
```

## License

[MIT](LICENSE).
