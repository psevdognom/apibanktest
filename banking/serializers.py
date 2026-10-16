from rest_framework import serializers
from .models import Transaction


class BalanceSerializer(serializers.Serializer):
    account_number = serializers.CharField()
    balance = serializers.DecimalField(max_digits=12, decimal_places=2)


class TransactionSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(source='created_at')

    class Meta:
        model = Transaction
        fields = ('amount', 'type', 'timestamp')


class TransferSerializer(serializers.Serializer):
    to_account_number = serializers.RegexField(regex=r'^\d{10}$')
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)

    def validate_amount(self, amount):
        if amount <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return amount


class TransferResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    transferred_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    fee = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_debited = serializers.DecimalField(max_digits=12, decimal_places=2)
    new_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
