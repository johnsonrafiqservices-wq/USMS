from django.contrib import admin
from accounts.admin import BaseAdmin
from .models import (
    Campus, Faculty, Department, Programme, AcademicSession,
    Course, CourseAllocation, Timetable, Attendance, GradeScale,
    AcademicCalendarEvent, ExamType, ExamScore, StudentResult, Intake,
    StudyYear, StudySemester, StudyLevel
)


@admin.register(StudyYear)
class StudyYearAdmin(BaseAdmin):
    list_display = ['code', 'name', 'level']
    list_filter = ['level']
    search_fields = ['code', 'name']


@admin.register(StudySemester)
class StudySemesterAdmin(BaseAdmin):
    list_display = ['code', 'name', 'number']
    list_filter = ['number']
    search_fields = ['code', 'name']


@admin.register(StudyLevel)
class StudyLevelAdmin(BaseAdmin):
    list_display = ['code', 'name', 'level_number', 'is_active', 'programme_count']
    list_filter = ['is_active', 'level_number']
    search_fields = ['name', 'code']
    ordering = ['level_number']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'level_number', 'description', 'is_active')
        }),
    )
    
    def programme_count(self, obj):
        return obj.programmes.count()
    programme_count.short_description = 'Programmes'


@admin.register(Campus)
class CampusAdmin(BaseAdmin):
    list_display = ['code', 'name', 'location', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code', 'location']
    
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'location', 'address', 'phone', 'email', 'is_active')
        }),
    )


@admin.register(Faculty)
class FacultyAdmin(BaseAdmin):
    list_display = ['code', 'name', 'campus', 'dean', 'is_active']
    list_filter = ['campus', 'is_active']
    search_fields = ['name', 'code']
    
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'campus', 'dean', 'description', 'established_date', 'is_active')
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'campus' in form.base_fields:
            form.base_fields['campus'].required = False
        return form


@admin.register(Department)
class DepartmentAdmin(BaseAdmin):
    list_display = ['code', 'name', 'faculty', 'head_of_department', 'is_active']
    list_filter = ['faculty', 'is_active']
    search_fields = ['name', 'code']


@admin.register(Programme)
class ProgrammeAdmin(BaseAdmin):
    list_display = ['code', 'name', 'department', 'level', 'schedule', 'duration_years']
    list_filter = ['level', 'schedule', 'department']
    search_fields = ['name', 'code']


@admin.register(AcademicSession)
class AcademicSessionAdmin(BaseAdmin):
    list_display = ['name', 'is_current', 'created_at']
    list_filter = ['is_current']
    search_fields = ['name']

    fieldsets = (
        (None, {
            'fields': ('name', 'is_current')
        }),
    )


@admin.register(Intake)
class IntakeAdmin(BaseAdmin):
    list_display = ['code', 'name', 'student_count', 'created_at']
    list_filter = []
    search_fields = ['code', 'name']

    fieldsets = (
        (None, {
            'fields': ('code', 'name')
        }),
    )

    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = 'Students'


@admin.register(Course)
class CourseAdmin(BaseAdmin):
    list_display = ['code', 'title', 'department', 'credit_units', 'course_type', 'level']
    list_filter = ['department', 'course_type', 'level', 'is_active']
    search_fields = ['code', 'title']


@admin.register(CourseAllocation)
class CourseAllocationAdmin(BaseAdmin):
    list_display = ['course', 'lecturer', 'semester', 'is_active']
    list_filter = ['semester', 'is_active']


@admin.register(Timetable)
class TimetableAdmin(BaseAdmin):
    list_display = ['course_allocation', 'day', 'start_time', 'end_time', 'room']
    list_filter = ['day']


@admin.register(Attendance)
class AttendanceAdmin(BaseAdmin):
    list_display = ['student', 'course_allocation', 'date', 'is_present']
    list_filter = ['is_present', 'date']


@admin.register(GradeScale)
class GradeScaleAdmin(BaseAdmin):
    list_display = ['grade', 'min_score', 'max_score', 'grade_point', 'description']


@admin.register(AcademicCalendarEvent)
class AcademicCalendarEventAdmin(BaseAdmin):
    list_display = ['title', 'event_type', 'session', 'start_date', 'end_date', 'is_active']
    list_filter = ['event_type', 'session', 'is_active']
    search_fields = ['title']


@admin.register(ExamType)
class ExamTypeAdmin(BaseAdmin):
    list_display = ['name', 'category', 'weight', 'max_score', 'is_active']
    list_filter = ['category', 'is_active']


@admin.register(ExamScore)
class ExamScoreAdmin(BaseAdmin):
    list_display = ['student', 'course_allocation', 'exam_type', 'score']
    list_filter = ['exam_type', 'course_allocation__semester']
    search_fields = ['student__student_id']


@admin.register(StudentResult)
class StudentResultAdmin(BaseAdmin):
    list_display = ['student', 'course_allocation', 'total_score', 'grade', 'grade_point', 'approval_status', 'is_published']
    list_filter = ['approval_status', 'is_published', 'is_resit', 'grade']
    search_fields = ['student__student_id']
    readonly_fields = ['hod_approved_at', 'registrar_approved_at', 'published_at', 'created_at', 'updated_at']
