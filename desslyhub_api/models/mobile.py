from decimal import Decimal
from typing import Any

from desslyhub_api.models.base import DesslyHubModel


class MobileGame(DesslyHubModel):
    """Краткое описание мобильной игры в каталоге."""

    id: int
    name: str


class MobilePosition(DesslyHubModel):
    """Позиция (номинал) для пополнения мобильной игры."""

    id: int
    name: str
    price: Decimal


class MobileGameDetails(DesslyHubModel):
    """Подробная информация о мобильной игре."""

    id: int
    name: str
    positions: list[MobilePosition]
    fields: dict[str, Any] = {}
    servers: dict[str, Any] = {}
