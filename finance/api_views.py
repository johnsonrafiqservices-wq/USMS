from rest_framework import viewsets, permissions
from .models import Invoice, Payment
from .serializers import InvoiceSerializer, PaymentSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    filterset_fields = ['student', 'status', 'session']
    search_fields = ['invoice_number', 'student__student_id']


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filterset_fields = ['student', 'status', 'payment_method']


class FinanceStatsView(APIView):
    """Return monthly aggregates for payments and invoices for the last 12 months."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        now = timezone.now()
        start = (now - timedelta(days=365)).replace(day=1)

        pay_qs = (
            Payment.objects.filter(status='completed', payment_date__gte=start)
            .annotate(month=TruncMonth('payment_date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )

        inv_qs = (
            Invoice.objects.filter(issued_date__gte=start)
            .annotate(month=TruncMonth('issued_date'))
            .values('month')
            .annotate(total=Sum('total_amount'))
            .order_by('month')
        )

        # normalize to YYYY-MM keys
        pay_map = {item['month'].strftime('%Y-%m'): float(item['total'] or 0) for item in pay_qs}
        inv_map = {item['month'].strftime('%Y-%m'): float(item['total'] or 0) for item in inv_qs}

        labels = []
        payments = []
        invoices = []

        cur = start
        while cur <= now:
            key = cur.strftime('%Y-%m')
            labels.append(cur.strftime('%b %Y'))
            payments.append(round(pay_map.get(key, 0.0), 2))
            invoices.append(round(inv_map.get(key, 0.0), 2))
            # increment month
            if cur.month == 12:
                cur = cur.replace(year=cur.year + 1, month=1)
            else:
                cur = cur.replace(month=cur.month + 1)

        return Response({'labels': labels, 'payments': payments, 'invoices': invoices})
