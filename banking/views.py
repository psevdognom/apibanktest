from django.db import transaction
from django.utils.dateparse import parse_datetime
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import BankAccount, Transaction
from .serializers import (
    BalanceSerializer,
    TransactionSerializer,
    TransferResponseSerializer,
    TransferSerializer,
)
from .services import calculate_transfer_fee, quantize_money


class BalanceView(APIView):
    @extend_schema(
        summary='Get current balance',
        responses={200: BalanceSerializer},
        tags=['accounts'],
    )
    def get(self, request):
        account = request.user.bank_account
        serializer = BalanceSerializer(
            {
                'account_number': account.account_number,
                'balance': account.balance,
            }
        )
        return Response(serializer.data)


class TransactionListView(APIView):
    @extend_schema(
        summary='List transactions',
        description='Returns transactions of the authenticated user. Optional query parameters filter by ISO datetime range.',
        parameters=[
            OpenApiParameter(name='from', type=str, location=OpenApiParameter.QUERY, description='ISO datetime lower bound'),
            OpenApiParameter(name='to', type=str, location=OpenApiParameter.QUERY, description='ISO datetime upper bound'),
        ],
        responses={200: TransactionSerializer(many=True), 400: OpenApiResponse(description='Invalid datetime filter')},
        tags=['transactions'],
    )
    def get(self, request):
        queryset = request.user.bank_account.transactions.all()
        from_param = request.query_params.get('from')
        to_param = request.query_params.get('to')

        if from_param:
            from_dt = parse_datetime(from_param)
            if not from_dt:
                return Response({'detail': 'Invalid from datetime'}, status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(created_at__gte=from_dt)

        if to_param:
            to_dt = parse_datetime(to_param)
            if not to_dt:
                return Response({'detail': 'Invalid to datetime'}, status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(created_at__lte=to_dt)

        serializer = TransactionSerializer(queryset, many=True)
        return Response(serializer.data)


class TransferView(APIView):
    @extend_schema(
        summary='Transfer money',
        description='Transfers money to another account. Applies a 2.5% fee with a minimum fee of €5. Records debit and credit transactions atomically.',
        request=TransferSerializer,
        responses={
            200: TransferResponseSerializer,
            400: OpenApiResponse(description='Validation error, insufficient funds, or self-transfer'),
            404: OpenApiResponse(description='Receiver account not found'),
        },
        tags=['transfers'],
    )
    def post(self, request):
        serializer = TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = quantize_money(serializer.validated_data['amount'])
        destination_number = serializer.validated_data['to_account_number']

        with transaction.atomic():
            sender = BankAccount.objects.select_for_update().get(user=request.user)
            receiver = BankAccount.objects.select_for_update().filter(account_number=destination_number).first()

            if receiver is None:
                return Response({'detail': 'Receiver account not found'}, status=status.HTTP_404_NOT_FOUND)

            if sender.id == receiver.id:
                return Response({'detail': 'Cannot transfer to your own account'}, status=status.HTTP_400_BAD_REQUEST)

            fee = calculate_transfer_fee(amount)
            total = quantize_money(amount + fee)

            if sender.balance < total:
                return Response({'detail': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)

            sender.balance = quantize_money(sender.balance - total)
            receiver.balance = quantize_money(receiver.balance + amount)
            sender.save(update_fields=['balance'])
            receiver.save(update_fields=['balance'])

            Transaction.objects.create(
                account=sender,
                amount=amount,
                type=Transaction.Type.DEBIT,
                description=f'Transfer to {receiver.account_number}',
            )
            Transaction.objects.create(
                account=sender,
                amount=fee,
                type=Transaction.Type.DEBIT,
                description=f'Transfer fee for {receiver.account_number}',
            )
            Transaction.objects.create(
                account=receiver,
                amount=amount,
                type=Transaction.Type.CREDIT,
                description=f'Transfer from {sender.account_number}',
            )

        return Response(
            {
                'message': 'Transfer completed successfully',
                'transferred_amount': f'{amount:.2f}',
                'fee': f'{fee:.2f}',
                'total_debited': f'{total:.2f}',
                'new_balance': f'{sender.balance:.2f}',
            },
            status=status.HTTP_200_OK,
        )
