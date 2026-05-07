from django.contrib import admin
from accounts.admin import BaseAdmin
from .models import StaffProfile, StaffPerformance, Payroll, LeaveType, LeaveRequest, Document


@admin.register(StaffProfile)
class StaffProfileAdmin(BaseAdmin):
    list_display = ['staff_id', 'user', 'department', 'staff_type', 'rank', 'is_active']
    list_filter = ['staff_type', 'rank', 'department', 'is_active']
    search_fields = ['staff_id', 'user__first_name', 'user__last_name']


@admin.register(StaffPerformance)
class StaffPerformanceAdmin(BaseAdmin):
    list_display = ['staff', 'semester', 'overall_rating', 'teaching_score']
    list_filter = ['semester']


@admin.register(Payroll)
class PayrollAdmin(BaseAdmin):
    list_display = ['staff', 'month', 'basic_salary', 'net_pay', 'status', 'payment_date']
    list_filter = ['status', 'month']
    search_fields = ['staff__staff_id', 'staff__user__first_name', 'staff__user__last_name']
    readonly_fields = ['net_pay', 'created_at']

    fieldsets = (
        ('Staff & Period', {'fields': ('staff', 'month', 'status', 'payment_date')}),
        ('Earnings', {'fields': ('basic_salary', 'housing_allowance', 'transport_allowance', 'other_allowances')}),
        ('Deductions', {'fields': ('tax_deduction', 'nssf_deduction', 'other_deductions')}),
        ('Summary', {'fields': ('net_pay', 'approved_by', 'remarks', 'created_at')}),
    )


@admin.register(LeaveType)
class LeaveTypeAdmin(BaseAdmin):
    list_display = ['name', 'max_days_per_year', 'is_paid', 'requires_approval']


@admin.register(LeaveRequest)
class LeaveRequestAdmin(BaseAdmin):
    list_display = ['staff', 'leave_type', 'start_date', 'end_date', 'status', 'days_requested']
    list_filter = ['status', 'leave_type']
    search_fields = ['staff__staff_id', 'staff__user__first_name', 'staff__user__last_name']
    readonly_fields = ['applied_at', 'reviewed_at']


@admin.register(Document)
class DocumentAdmin(BaseAdmin):
    list_display = ['title', 'document_type', 'owner_type', 'is_verified', 'uploaded_at']
    list_filter = ['document_type', 'owner_type', 'is_verified']
    search_fields = ['title', 'student__student_id', 'staff__staff_id']
