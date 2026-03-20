from decimal import Decimal

from django.conf import settings
from django.contrib.auth import authenticate
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import (
    AuthService,
    LoginSerializer,
    RegisterResponseSerializer,
    RegisterSerializer,
    TokenPairSerializer,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Register a new user',
        description='Creates a user, automatically creates a bank account, and deposits the €10,000 welcome bonus.',
        request=RegisterSerializer,
        responses={201: RegisterResponseSerializer, 400: OpenApiResponse(description='Validation error')},
        tags=['auth'],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = AuthService.token_pair_for_user(user)
        return Response(
            {
                'message': 'User registered successfully',
                'account_number': user.bank_account.account_number,
                'welcome_bonus': str(Decimal(settings.WELCOME_BONUS).quantize(Decimal('0.01'))),
                **tokens,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Log in',
        description='Authenticates a user and returns a JWT access and refresh token pair.',
        request=LoginSerializer,
        responses={200: TokenPairSerializer, 401: OpenApiResponse(description='Invalid credentials')},
        tags=['auth'],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
        )
        if not user:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(AuthService.token_pair_for_user(user), status=status.HTTP_200_OK)
