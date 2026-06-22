from enum import StrEnum


class ServiceType(StrEnum):
    """Тип сервиса, для которого создаётся заказ."""

    STEAM_REFILL = "steam_refill"
    STEAM_GIFT = "steam_gift"
    VOUCHER = "voucher"
    MOBILE_REFILL = "mobile_refill"
    ESIM = "esim"


class PaymentMethod(StrEnum):
    """Способ оплаты заказа."""

    BALANCE = "balance"
    PAYLINK_QR = "paylink_qr"
