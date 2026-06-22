from pydantic import Field

from desslyhub_api.models.base import DesslyHubModel


class ExchangeRate(DesslyHubModel):
    """Курс одной валюты к доллару США для пополнения Steam."""

    rate: float = Field(alias="exchange_rate")


class ExchangeRates(DesslyHubModel):
    """Курсы всех поддерживаемых валют: код валюты сопоставлен с курсом."""

    rates: dict[int, float] = Field(alias="exchange_rates")
