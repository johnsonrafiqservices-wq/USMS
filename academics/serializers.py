from rest_framework import serializers
from .models import (
    Department, Course, AcademicSession, StudySemester, Faculty, Programme,
    AcademicCalendarEvent, ExamType, ExamScore, StudentResult, GradeScale
)


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'name', 'code', 'description', 'is_active']


class DepartmentSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'faculty', 'faculty_name', 'description', 'is_active']


class CourseSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'code', 'title', 'department', 'department_name',
                  'credit_units', 'course_type', 'level', 'semester',
                  'max_students', 'is_active']


class StudySemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudySemester
        fields = ['id', 'code', 'name', 'number']


class AcademicSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicSession
        fields = ['id', 'name', 'is_current', 'created_at']


class AcademicCalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicCalendarEvent
        fields = ['id', 'title', 'event_type', 'session', 'semester',
                  'start_date', 'end_date', 'description', 'is_active']


class ExamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamType
        fields = ['id', 'name', 'category', 'weight', 'max_score', 'is_active']


class ExamScoreSerializer(serializers.ModelSerializer):
    exam_type_name = serializers.CharField(source='exam_type.name', read_only=True)
    course_code = serializers.CharField(source='course_allocation.course.code', read_only=True)

    class Meta:
        model = ExamScore
        fields = ['id', 'student', 'course_allocation', 'course_code',
                  'exam_type', 'exam_type_name', 'score', 'remarks']


class StudentResultSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source='course_allocation.course.code', read_only=True)
    course_title = serializers.CharField(source='course_allocation.course.title', read_only=True)

    class Meta:
        model = StudentResult
        fields = ['id', 'student', 'course_allocation', 'course_code', 'course_title',
                  'ca_score', 'exam_score', 'total_score', 'grade', 'grade_point',
                  'is_resit', 'approval_status', 'is_published']
