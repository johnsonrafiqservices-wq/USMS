from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import StaffProfile, Payroll, LeaveRequest, Document
from .serializers import StaffProfileSerializer, PayrollSerializer, LeaveRequestSerializer, DocumentSerializer


class StaffProfileViewSet(viewsets.ModelViewSet):
    queryset = StaffProfile.objects.select_related('user', 'department').all()
    serializer_class = StaffProfileSerializer
    filterset_fields = ['staff_type', 'department', 'is_active']
    search_fields = ['staff_id', 'user__first_name', 'user__last_name']


class PayrollViewSet(viewsets.ModelViewSet):
    queryset = Payroll.objects.select_related('staff__user').all()
    serializer_class = PayrollSerializer
    filterset_fields = ['staff', 'status']

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        payroll = self.get_object()
        if payroll.status != Payroll.Status.DRAFT:
            return Response({'error': 'Only draft payrolls can be approved.'}, status=400)
        payroll.status = Payroll.Status.APPROVED
        payroll.approved_by = request.user
        payroll.save()
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'], url_path='mark-paid')
    def mark_paid(self, request, pk=None):
        payroll = self.get_object()
        if payroll.status != Payroll.Status.APPROVED:
            return Response({'error': 'Only approved payrolls can be marked as paid.'}, status=400)
        payroll.status = Payroll.Status.PAID
        payroll.payment_date = timezone.now().date()
        payroll.save()
        return Response({'status': 'paid'})


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.select_related('staff__user', 'leave_type').all()
    serializer_class = LeaveRequestSerializer
    filterset_fields = ['staff', 'status', 'leave_type']

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status = LeaveRequest.Status.APPROVED
        leave.reviewed_by = request.user
        leave.review_remarks = request.data.get('remarks', '')
        leave.reviewed_at = timezone.now()
        leave.save()
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        leave = self.get_object()
        leave.status = LeaveRequest.Status.REJECTED
        leave.reviewed_by = request.user
        leave.review_remarks = request.data.get('remarks', '')
        leave.reviewed_at = timezone.now()
        leave.save()
        return Response({'status': 'rejected'})


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    filterset_fields = ['document_type', 'owner_type', 'is_verified']
