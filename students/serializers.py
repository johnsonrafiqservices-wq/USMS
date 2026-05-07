from rest_framework import serializers
from .models import Student, AcademicYearEnrollment, Enrollment, AdmissionApplication


class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    programme_name = serializers.CharField(source='programme.name', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'student_id', 'full_name', 'programme', 'programme_name',
                  'current_year', 'current_semester_number', 'level_display',
                  'status', 'admission_date', 'expected_graduation']

    def get_full_name(self, obj) -> str:
        return obj.user.get_full_name()


class AcademicYearEnrollmentSerializer(serializers.ModelSerializer):
    session_name = serializers.CharField(source='academic_session.name', read_only=True)
    label = serializers.ReadOnlyField()

    class Meta:
        model = AcademicYearEnrollment
        fields = ['id', 'student', 'academic_session', 'session_name', 'semester',
                  'year_of_study', 'semester_number', 'label', 'status',
                  'enrolled_by', 'enrollment_date', 'remarks']


class EnrollmentSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source='course.code', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'course_code', 'course_title',
                  'semester', 'academic_year_enrollment', 'enrollment_date', 'is_active']
