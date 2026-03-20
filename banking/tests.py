from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from banking.models import BankAccount, Transaction


class BankingTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='sender@example.com', password='strongpass123')
        self.user2 = User.objects.create_user(email='receiver@example.com', password='strongpass123')
        self.account1 = BankAccount.objects.create(user=self.user1, account_number='1111111111', balance='10000.00')
        self.account2 = BankAccount.objects.create(user=self.user2, account_number='2222222222', balance='100.00')
        self.token = str(RefreshToken.for_user(self.user1).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_balance_endpoint(self):
        response = self.client.get('/api/accounts/me/balance/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['account_number'], '1111111111')
        self.assertEqual(response.data['balance'], '10000.00')

    def test_transfer_endpoint_updates_balances_and_transactions(self):
        response = self.client.post(
            '/api/transfers/',
            {'to_account_number': '2222222222', 'amount': '100.00'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.account1.refresh_from_db()
        self.account2.refresh_from_db()
        self.assertEqual(str(self.account1.balance), '9895.00')
        self.assertEqual(str(self.account2.balance), '200.00')
        self.assertEqual(Transaction.objects.filter(account=self.account1).count(), 2)
        self.assertEqual(Transaction.objects.filter(account=self.account2).count(), 1)


    def test_transfer_fails_on_insufficient_funds(self):
        response = self.client.post(
            '/api/transfers/',
            {'to_account_number': '2222222222', 'amount': '999999.00'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Insufficient funds')
