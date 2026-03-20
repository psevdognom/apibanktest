from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from banking.models import BankAccount, Transaction


class AuthTests(APITestCase):
    def test_register_creates_account_and_welcome_bonus(self):
        response = self.client.post(
            '/api/auth/register/',
            {'email': 'user1@example.com', 'password': 'strongpass123'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='user1@example.com').exists())
        user = User.objects.get(email='user1@example.com')
        self.assertTrue(hasattr(user, 'bank_account'))
        self.assertEqual(str(user.bank_account.balance), '10000.00')
        self.assertEqual(len(user.bank_account.account_number), 10)
        self.assertEqual(Transaction.objects.filter(account=user.bank_account).count(), 1)

    def test_login_returns_tokens(self):
        User.objects.create_user(email='user2@example.com', password='strongpass123')
        response = self.client.post(
            '/api/auth/login/',
            {'email': 'user2@example.com', 'password': 'strongpass123'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
