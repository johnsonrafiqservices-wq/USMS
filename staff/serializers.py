from rest_framework import serializers
from .models import StaffProfile, StaffPerformance, Payroll, LeaveType, LeaveRequest, Document


class StaffProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = StaffProfile
        fields = ['id', 'staff_id', 'full_name', 'department', 'department_name',
                  'staff_type', 'rank', 'specialization', 'is_active']

    def get_full_name(self, obj) -> str:
        return obj.user.get_full_name()


class PayrollSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff.user.get_full_name', read_only=True)
    month_display = serializers.SerializerMethodField()

    class Meta:
        model = Payroll
        fields = ['id', 'staff', 'staff_name', 'month', 'month_display',
                  'basic_salary', 'housing_allowance', 'transport_allowance',
                  'other_allowances', 'tax_deduction', 'nssf_deduction',
                  'other_deductions', 'net_pay', 'status', 'payment_date']
        read_only_fields = ['net_pay']

    def get_month_display(self, obj) -> str:
        return obj.month.strftime('%B %Y')


class LeaveRequestSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff.user.get_full_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    days_requested = serializers.ReadOnlyField()

    class Meta:
        model = LeaveRequest
        fields = ['id', 'staff', 'staff_name', 'leave_type', 'leave_type_name',
                  'start_date', 'end_date', 'days_requested', 'reason',
                  'status', 'review_remarks', 'applied_at']


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'document_type', 'owner_type', 'student', 'staff',
                  'file', 'description', 'is_verified', 'uploaded_at']
