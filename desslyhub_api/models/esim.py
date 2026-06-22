from typing import Any

from desslyhub_api.models.base import DesslyHubModel


class VariantAttributes(DesslyHubModel):
    """Атрибуты варианта eSIM: тип пакета, география и страны."""

    esim_package_type: str
    geo_scope: str
    continent: str = ""
    country: str = ""
    esim_countries: list[str] = []


class EsimVariant(DesslyHubModel):
    """Вариант eSIM в списке каталога."""

    id: str
    name: str
    description: str
    image: str
    attributes: VariantAttributes


class EsimProductList(DesslyHubModel):
    """Страница списка вариантов eSIM с курсорами пагинации."""

    variants: list[EsimVariant]
    next_cursor: str = ""
    prev_cursor: str = ""


class EsimProductVariant(DesslyHubModel):
    """Конкретный продукт внутри варианта eSIM: цена, остаток и лимиты."""

    id: str
    name: str
    description: str
    price: float
    stock: int
    max_per_order: int
    attributes: dict[str, Any] = {}


class EsimProductDetails(DesslyHubModel):
    """Подробная информация о варианте eSIM с доступными продуктами."""

    id: str
    name: str
    description: str
    image: str
    attributes: VariantAttributes
    products: list[EsimProductVariant]
