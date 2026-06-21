from django.contrib import admin
from accounts.admin import BaseAdmin
from .models import FeeStructure, Invoice, InvoiceItem, Payment, Scholarship


@admin.register(FeeStructure)
class FeeStructureAdmin(BaseAdmin):
    list_display = ['name', 'fee_type', 'get_programmes', 'get_faculties', 'amount', 'session', 'is_mandatory']
    list_filter = ['fee_type', 'session', 'is_mandatory', 'faculties']
    filter_horizontal = ['programmes', 'faculties', 'departments', 'courses']

    def get_programmes(self, obj):
        """Display linked programmes or 'All'."""
        if obj.programmes.exists():
            return ", ".join([p.code for p in obj.programmes.all()[:3]])
        return "All Programmes"
    get_programmes.short_description = 'Programmes'

    def get_faculties(self, obj):
        """Display linked faculties or 'All'."""
        if obj.faculties.exists():
            return ", ".join([f.code for f in obj.faculties.all()[:3]])
        return "All Faculties"
    get_faculties.short_description = 'Faculties'


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
