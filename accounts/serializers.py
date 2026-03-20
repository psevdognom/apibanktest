from decimal import Decimal
from django.conf import settings
from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from banking.models import BankAccount, Transaction
from banking.services import generate_account_number


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8, max_length=128)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already registered.')
        return value

    def create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
            )
            account_number = generate_account_number()
            account = BankAccount.objects.create(
                user=user,
                account_number=account_number,
                balance=Decimal(settings.WELCOME_BONUS),
            )
            Transaction.objects.create(
                account=account,
                amount=Decimal(settings.WELCOME_BONUS),
                type=Transaction.Type.CREDIT,
                description='Welcome bonus',
            )
            return user


class RegisterResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    account_number = serializers.CharField()
    welcome_bonus = serializers.DecimalField(max_digits=12, decimal_places=2)
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class TokenPairSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()


class AuthService:
    @staticmethod
    def token_pair_for_user(user):
        refresh = RefreshToken.for_user(user)
        return {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }
