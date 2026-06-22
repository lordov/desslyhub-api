<p align="center">
  <img src="https://raw.githubusercontent.com/lordov/desslyhub/main/assets/logo.svg" alt="DesslyHub API" width="320">
</p>

<h1 align="center">desslyhub-api</h1>

<p align="center">
  Асинхронный Python-клиент для <a href="https://desslyhub.com/readme/">DesslyHub API</a>:<br>
  Steam, мобильные игры, ваучеры, eSIM, баланс мерчанта, заказы и курсы валют.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12%2B-3776AB?logo=python&logoColor=white" alt="Python 3.12+">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT">
  <img src="https://img.shields.io/badge/code%20style-black-000000" alt="black">
  <img src="https://img.shields.io/badge/types-mypy-2A6DB2" alt="mypy">
  <img src="https://img.shields.io/badge/async-aiohttp%20%2B%20orjson-FF69B4" alt="aiohttp + orjson">
</p>

---

Клиент построен на `aiohttp` + `orjson`, ответы валидируются через `pydantic`, денежные значения представлены типом `Decimal`. Все эндпоинты доступны под базовым URL `https://desslyhub.com` с префиксом `/api/v1/`.

## Содержание

- [Возможности](#возможности)
- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)
- [Аутентификация](#аутентификация)
- [Использование](#использование)
- [Заказы (Orders)](#заказы-orders)
- [Денежные значения и обработка ошибок](#денежные-значения-и-обработка-ошибок)
- [Разработка](#разработка)
- [Лицензия](#лицензия)

## Возможности

| Ресурс | Назначение |
| --- | --- |
| `client.steam` | Каталог игр для подарка, издания игры и проверка логина для пополнения. |
| `client.mobile` | Каталог мобильных игр и детали конкретной игры. |
| `client.vouchers` | Каталог товаров-ваучеров и товар по идентификатору. |
| `client.esim` | Каталог вариантов eSIM с курсорной пагинацией и детали варианта. |
| `client.merchant` | Текущий баланс мерчанта. |
| `client.exchange` | Курсы валют к доллару США для пополнения Steam. |
| `client.orders` | Единая точка создания всех покупок (пополнения, подарки, ваучеры, eSIM), а также список и детали заказов. |

> Создание любых покупок выполняется через ресурс `orders` (единый эндпоинт `POST /api/v1/orders`). Прежние методы `gift` / `top_up` / `refill` / `buy` и ресурс `merchants` с эндпоинтами `/transactions` удалены — историю и статусы покупок заменили заказы.

## Установка

**Требования:** Python 3.12+ и [uv](https://docs.astral.sh/uv/).

### Для конечных пользователей

```bash
uv add desslyhub-api
# или
pip install desslyhub-api
```

Импорт пакета: `import desslyhub_api`.

### Для локальной разработки

Клонируйте репозиторий и установите все группы зависимостей (включая dev-инструменты: pytest, black, isort, mypy):

```bash
uv sync --all-groups
```

## Быстрый старт

```python
import asyncio

from desslyhub_api import DesslyHubClient


async def main() -> None:
    async with DesslyHubClient("ВАШ_API_КЛЮЧ", "ВАШ_SECRET") as client:
        balance = await client.merchant.get_balance()
        print(balance.balance)  # Decimal


asyncio.run(main())
```

Клиент — асинхронный контекстный менеджер: внутри `async with` открывается постоянная HTTP-сессия, которая автоматически закрывается на выходе.

## Аутентификация

Каждый запрос подписывается по схеме HMAC-SHA256: `signature = HMAC_SHA256(secret, api_key + timestamp + body)`. Клиент сам добавляет к каждому запросу заголовки `X-Api-Key`, `X-Timestamp` (Unix-время в секундах) и `X-Signature`. Поэтому нужны **два** значения — `api_key` и `secret`. Базовый URL по умолчанию — `https://desslyhub.com`.

```python
from desslyhub_api import DesslyHubClient

# Минимальный вариант
client = DesslyHubClient("ВАШ_API_КЛЮЧ", "ВАШ_SECRET")

# С переопределением base_url и таймаута
client = DesslyHubClient(
    "ВАШ_API_КЛЮЧ",
    "ВАШ_SECRET",
    base_url="https://desslyhub.com",
    timeout_seconds=30.0,
)
```

## Использование

Все методы асинхронные и вызываются внутри `async with DesslyHubClient(api_key, secret) as client:`.

### Баланс мерчанта

```python
balance = await client.merchant.get_balance()
print(balance.balance)            # Decimal — общий баланс
print(balance.available_balance)  # Decimal — доступно для трат
print(balance.overdraft)          # Decimal — лимит овердрафта
print(balance.reserve)            # Decimal — зарезервированные средства
```

`get_balance()` возвращает модель `Balance` с полями `balance`, `available_balance`, `overdraft`, `reserve` — все значения типа `Decimal`.

### Steam: каталог игр, издания и проверка логина

```python
games = await client.steam.get_games()
for game in games:
    print(game)

# Издания конкретной игры по её app_id
editions = await client.steam.get_editions(app_id=730)
for edition in editions:
    print(edition)

# Можно ли пополнить аккаунт Steam с указанным логином
can_refill = await client.steam.check_login(username="steam_user")
print(can_refill)  # bool
```

### Mobile: каталог и детали игры

```python
games = await client.mobile.get_games()
for game in games:
    print(game)

details = await client.mobile.get_game(game_id=42)
print(details)
```

### Vouchers: каталог

```python
products = await client.vouchers.get_products()
for product in products:
    print(product)

product = await client.vouchers.get_product(product_id=10)
print(product)
```

### eSIM: каталог

```python
page = await client.esim.get_products()  # cursor=None — первая страница
for variant in page.variants:
    print(variant)

# Следующая страница по курсору
if page.next_cursor:
    next_page = await client.esim.get_products(cursor=page.next_cursor)
    print(next_page.variants)

details = await client.esim.get_product(variant_id="variant-123")
print(details)
```

### Exchange: курсы валют

```python
from desslyhub_api import Currency

all_rates = await client.exchange.get_all_rates()
print(all_rates.rates)  # dict[int, float]

# Курс по конкретной валюте (enum Currency или числовой код)
rate = await client.exchange.get_rate(Currency.RUB)
print(rate.rate)
```

## Заказы (Orders)

Все покупки создаются через ресурс `client.orders`. Каждый метод `create_*` возвращает `CreateOrderResponse` с полями `order_id` (int) и `status` (str). Типичный сценарий:

1. Создать заказ методом `create_*` — в ответе придут `order_id` и `status`.
2. Опрашивать заказ через `client.orders.get(order_id)`, отслеживая `order_status` и `service_result` (результат становится доступен после успешного выполнения).

У всех методов `create_*` есть общие необязательные параметры (только по ключу):

- `payment_method: PaymentMethod` — способ оплаты, по умолчанию `PaymentMethod.BALANCE` (списание с баланса мерчанта). Для оплаты по QR-ссылке — `PaymentMethod.PAYLINK_QR`.
- `payment_params: PaylinkQRPaymentParams | None` — параметры оплаты по QR (нужны для `PAYLINK_QR`).
- `reference: str | None` — ваш внешний идентификатор заказа.

### Оплата с баланса (по умолчанию)

```python
# Пополнение Steam
order = await client.orders.create_steam_refill(
    username="steam_user",
    amount=10.0,                 # сумма в USD
    reference="my-order-id",     # необязательно
)
print(order.order_id, order.status)

# Подарок игры Steam
order = await client.orders.create_steam_gift(
    invite_url="https://steamcommunity.com/p/...",
    package_id="12345",
    region="RU",
)

# Покупка ваучеров
order = await client.orders.create_voucher(
    root_id=10,
    variant_id=2,
    quantity=1,
)

# Пополнение мобильной игры
order = await client.orders.create_mobile_refill(
    position=3,
    fields={"player_id": "123456"},
)

# Покупка eSIM
order = await client.orders.create_esim(
    product_id="product-123",
    variant_id="variant-456",
)
```

### Оплата по QR-ссылке (PAYLINK_QR)

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

### Список и детали заказов

```python
# Страница списка с пагинацией limit/offset
page = await client.orders.list(limit=20, offset=0)
print(page.total, page.limit, page.offset)
for item in page.items:
    print(item.order_id, item.order_status)

# Подробности конкретного заказа
details = await client.orders.get(order_id=12345)
print(details.order_status)    # str — статус заказа
print(details.service_type)    # str — тип сервиса
print(details.commission)      # Decimal — комиссия
print(details.final_amount)    # Decimal — итоговая сумма
print(details.service_result)  # результат выполнения (после успеха)
```

`list()` возвращает `OrderList` с полями `items`, `total`, `limit`, `offset`. `get()` возвращает `OrderDetails` с полями `order_id`, `order_status`, `service_type`, `payment_method`, `commission` и `final_amount` (оба `Decimal`), временными метками и `service_result`.

## Денежные значения и обработка ошибок

- Денежные значения (например поля `Balance`, а также `commission` и `final_amount` в `OrderDetails`) представлены типом `Decimal`, чтобы избежать ошибок округления.
- При HTTP-статусе ответа `>= 400` клиент бросает `DesslyHubAPIError`. Тело ошибки разбирается в формате RFC 7807 (`ErrorModel`). У исключения есть атрибуты `error_code` (int), `message` (str) и `http_status` (int | None).
- Сетевые проблемы поднимают `DesslyHubConnectionError`.
- Некорректный/нечитаемый ответ API поднимает `DesslyHubResponseError`.
- Все исключения наследуются от базового `DesslyHubError`.

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
        print("Ошибка API:", error.error_code, error.message, error.http_status)
    except DesslyHubConnectionError as error:
        print("Ошибка соединения:", error)
    except DesslyHubResponseError as error:
        print("Некорректный ответ:", error)
```

## Разработка

Установка окружения со всеми dev-зависимостями (pytest, black, isort, mypy):

```bash
uv sync --all-groups
```

Полезные команды:

```bash
uv run pytest -q                   # тесты
uv run isort . && uv run black .   # форматирование
uv run mypy desslyhub_api          # проверка типов
```

## Лицензия

[MIT](LICENSE).
