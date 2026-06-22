from decimal import Decimal

from desslyhub_api.models.base import DesslyHubModel


class Balance(DesslyHubModel):
    """Баланс мерчанта: общий, доступный, овердрафт и резерв."""

    balance: Decimal
    available_balance: Decimal
    overdraft: Decimal
    reserve: Decimal
