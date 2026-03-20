import random
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from .models import BankAccount


TWOPLACES = Decimal('0.01')


def quantize_money(value: Decimal) -> Decimal:
    return Decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def calculate_transfer_fee(amount: Decimal) -> Decimal:
    amount = quantize_money(amount)
    fee = quantize_money(amount * Decimal(settings.TRANSFER_FEE_PERCENT))
    minimum = quantize_money(Decimal(settings.TRANSFER_FEE_MIN))
    return max(fee, minimum)


def generate_account_number() -> str:
    while True:
        number = ''.join(random.choices('0123456789', k=10))
        if not BankAccount.objects.filter(account_number=number).exists():
            return number
