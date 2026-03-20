from django.contrib import admin
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from accounts.views import LoginView, RegisterView
from banking.views import BalanceView, TransactionListView, TransferView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/accounts/me/balance/', BalanceView.as_view(), name='balance'),
    path('api/transactions/', TransactionListView.as_view(), name='transactions'),
    path('api/transfers/', TransferView.as_view(), name='transfer'),
]
