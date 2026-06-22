from decimal import Decimal

from desslyhub_api.models.base import DesslyHubModel


class SteamGiftGame(DesslyHubModel):
    """Краткое описание игры Steam в каталоге подарков."""

    app_id: int
    name: str


class SteamGiftRegionInfo(DesslyHubModel):
    """Цена и скидка издания игры Steam для конкретного региона."""

    region: str
    discount: str
    price: Decimal
    price_original: Decimal


class SteamGiftEdition(DesslyHubModel):
    """Издание игры Steam с идентификатором пакета и ценами по регионам."""

    edition: str
    package_id: int
    regions_info: list[SteamGiftRegionInfo]
