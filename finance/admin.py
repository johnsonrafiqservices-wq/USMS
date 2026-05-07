from django.contrib import admin
from accounts.admin import BaseAdmin
from .models import FeeStructure, Invoice, InvoiceItem, Payment, Scholarship


@admin.register(FeeStructure)
class FeeStructureAdmin(BaseAdmin):
    list_display = ['name', 'fee_type', 'programme', 'amount', 'session', 'is_mandatory']
    list_filter = ['fee_type', 'session', 'is_mandatory']


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(BaseAdmin):
    list_display = ['invoice_number', 'student', 'total_amount', 'amount_paid', 'balance', 'status']
    list_filter = ['status', 'session']
    search_fields = ['invoice_number', 'student__student_id']
    inlines = [InvoiceItemInline]


@admin.register(Payment)
class PaymentAdmin(BaseAdmin):
    list_display = ['receipt_number', 'student', 'amount', 'payment_method', 'status', 'payment_date']
    list_filter = ['status', 'payment_method']
    search_fields = ['receipt_number', 'student__student_id']


@admin.register(Scholarship)
class ScholarshipAdmin(BaseAdmin):
    list_display = ['name', 'student', 'amount', 'session', 'is_active']
    list_filter = ['session', 'is_active']
