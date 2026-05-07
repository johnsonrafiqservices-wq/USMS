from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Department, Course, AcademicSession, StudySemester, AcademicCalendarEvent, ExamType, ExamScore, StudentResult
from .serializers import (
    DepartmentSerializer, CourseSerializer, AcademicSessionSerializer,
    StudySemesterSerializer, AcademicCalendarEventSerializer,
    ExamTypeSerializer, ExamScoreSerializer, StudentResultSerializer
)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filterset_fields = ['faculty', 'is_active']
    search_fields = ['name', 'code']


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filterset_fields = ['department', 'level', 'course_type', 'is_active']
    search_fields = ['code', 'title']


class AcademicSessionViewSet(viewsets.ModelViewSet):
    queryset = AcademicSession.objects.all()
    serializer_class = AcademicSessionSerializer

    @action(detail=False, methods=['get'])
    def current(self, request):
        session = AcademicSession.objects.filter(is_current=True).first()
        if session:
            return Response(AcademicSessionSerializer(session).data)
        return Response({'detail': 'No current session set.'}, status=404)


class StudySemesterViewSet(viewsets.ModelViewSet):
    queryset = StudySemester.objects.all()
    serializer_class = StudySemesterSerializer
    filterset_fields = ['number']


class AcademicCalendarEventViewSet(viewsets.ModelViewSet):
    queryset = AcademicCalendarEvent.objects.all()
    serializer_class = AcademicCalendarEventSerializer
    filterset_fields = ['event_type', 'session', 'is_active']


class ExamTypeViewSet(viewsets.ModelViewSet):
    queryset = ExamType.objects.all()
    serializer_class = ExamTypeSerializer
    filterset_fields = ['category', 'is_active']


class ExamScoreViewSet(viewsets.ModelViewSet):
    queryset = ExamScore.objects.select_related('student', 'exam_type').all()
    serializer_class = ExamScoreSerializer
    filterset_fields = ['student', 'exam_type', 'course_allocation']


class StudentResultViewSet(viewsets.ModelViewSet):
    queryset = StudentResult.objects.select_related('student', 'course_allocation__course').all()
    serializer_class = StudentResultSerializer
    filterset_fields = ['student', 'approval_status', 'is_published', 'is_resit']

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        result = self.get_object()
        result.approval_status = StudentResult.ApprovalStatus.SUBMITTED
        result.save()
        return Response({'status': 'submitted'})

    @action(detail=True, methods=['post'], url_path='approve-hod')
    def approve_hod(self, request, pk=None):
        result = self.get_object()
        result.approval_status = StudentResult.ApprovalStatus.HOD_APPROVED
        result.approved_by_hod = request.user
        result.hod_approved_at = timezone.now()
        result.save()
        return Response({'status': 'hod_approved'})

    @action(detail=True, methods=['post'], url_path='approve-registrar')
    def approve_registrar(self, request, pk=None):
        result = self.get_object()
        result.approval_status = StudentResult.ApprovalStatus.REGISTRAR_APPROVED
        result.approved_by_registrar = request.user
        result.registrar_approved_at = timezone.now()
        result.save()
        return Response({'status': 'registrar_approved'})

    @action(detail=True, methods=['post'], url_path='publish')
    def publish(self, request, pk=None):
        result = self.get_object()
        result.approval_status = StudentResult.ApprovalStatus.PUBLISHED
        result.is_published = True
        result.published_at = timezone.now()
        result.save()
        return Response({'status': 'published'})

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        result = self.get_object()
        result.approval_status = StudentResult.ApprovalStatus.REJECTED
        result.rejection_reason = request.data.get('reason', '')
        result.save()
        return Response({'status': 'rejected'})
