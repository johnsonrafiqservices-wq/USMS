from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

app_name = 'finance_api'

router = DefaultRouter()
router.register(r'invoices', api_views.InvoiceViewSet)
router.register(r'payments', api_views.PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', api_views.FinanceStatsView.as_view(), name='stats'),
]
