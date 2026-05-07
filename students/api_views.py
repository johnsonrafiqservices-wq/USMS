from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Student, AcademicYearEnrollment, Enrollment
from .serializers import StudentSerializer, AcademicYearEnrollmentSerializer, EnrollmentSerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('user', 'programme').all()
    serializer_class = StudentSerializer
    filterset_fields = ['status', 'current_year', 'current_semester_number', 'programme']
    search_fields = ['student_id', 'user__first_name', 'user__last_name']

    @action(detail=True, methods=['get'], url_path='graduation-eligibility')
    def graduation_eligibility(self, request, pk=None):
        student = self.get_object()
        return Response(student.check_graduation_eligibility())

    @action(detail=True, methods=['get'])
    def transcript(self, request, pk=None):
        student = self.get_object()
        from academics.models import StudentResult
        results = StudentResult.objects.filter(
            student=student, is_published=True
        ).select_related('course_allocation__course', 'course_allocation__semester')
        data = {
            'student': StudentSerializer(student).data,
            'cgpa': student.calculate_cgpa(),
            'results': [
                {
                    'course': r.course_allocation.course.code,
                    'title': r.course_allocation.course.title,
                    'credits': r.course_allocation.course.credit_units,
                    'grade': r.grade,
                    'grade_point': float(r.grade_point),
                    'semester': str(r.course_allocation.semester),
                }
                for r in results
            ]
        }
        return Response(data)


class AcademicYearEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = AcademicYearEnrollment.objects.select_related('student', 'academic_session').all()
    serializer_class = AcademicYearEnrollmentSerializer
    filterset_fields = ['student', 'academic_session', 'year_of_study', 'semester_number', 'status']

    def perform_create(self, serializer):
        serializer.save(enrolled_by=self.request.user)


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    filterset_fields = ['student', 'semester', 'is_active']
