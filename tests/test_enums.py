import pytest

from desslyhub_api.enums.currency import Currency
from desslyhub_api.enums.orders import PaymentMethod, ServiceType


@pytest.mark.parametrize(
    ("currency", "code"),
    [
        (Currency.USD, 1),
        (Currency.GBP, 2),
        (Currency.EUR, 3),
        (Currency.RUB, 5),
        (Currency.UAH, 18),
    ],
)
def test_currency_codes(currency: Currency, code: int) -> None:
    """Коды валют совпадают со справочником DesslyHub и приводятся к int."""
    result = int(currency)

    assert result == code


@pytest.mark.parametrize(
    ("service_type", "value"),
    [
        (ServiceType.STEAM_REFILL, "steam_refill"),
        (ServiceType.STEAM_GIFT, "steam_gift"),
        (ServiceType.VOUCHER, "voucher"),
        (ServiceType.MOBILE_REFILL, "mobile_refill"),
        (ServiceType.ESIM, "esim"),
    ],
)
def test_service_type_values(service_type: ServiceType, value: str) -> None:
    """Строковые значения типов сервиса соответствуют ожидаемым."""
    result = str(service_type)

    assert result == value


@pytest.mark.parametrize(
    ("payment_method", "value"),
    [
        (PaymentMethod.BALANCE, "balance"),
        (PaymentMethod.PAYLINK_QR, "paylink_qr"),
    ],
)
def test_payment_method_values(payment_method: PaymentMethod, value: str) -> None:
    """Строковые значения способов оплаты соответствуют ожидаемым."""
    result = str(payment_method)

    assert result == value
