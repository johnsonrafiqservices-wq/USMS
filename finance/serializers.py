from rest_framework import serializers
from .models import Invoice, Payment, FeeStructure


class InvoiceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = Invoice
        fields = ['id', 'invoice_number', 'student', 'student_name', 'session',
                  'total_amount', 'amount_paid', 'balance', 'status', 'due_date']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'receipt_number', 'invoice', 'student', 'amount',
                  'payment_method', 'reference_number', 'status', 'payment_date']
