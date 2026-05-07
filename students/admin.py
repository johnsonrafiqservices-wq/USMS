from django.contrib import admin
from accounts.admin import BaseAdmin
from .models import Student, AcademicYearEnrollment, Enrollment, AdmissionApplication


class AcademicYearEnrollmentInline(admin.TabularInline):
    model = AcademicYearEnrollment
    extra = 0
    fields = ['academic_session', 'year_of_study', 'semester_number', 'semester', 'status', 'remarks']


@admin.register(Student)
class StudentAdmin(BaseAdmin):
    list_display = ['student_id', 'user', 'programme', 'current_year', 'current_semester_number', 'status']
    list_filter = ['status', 'current_year', 'current_semester_number', 'programme']
    search_fields = ['student_id', 'user__first_name', 'user__last_name']
    inlines = [AcademicYearEnrollmentInline]

    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'student_id', 'nationality', 'state_of_origin', 'lga')
        }),
        ('Academic Information', {
            'fields': ('programme', 'current_year', 'current_semester_number', 'intake', 'admission_date', 'expected_graduation', 'status')
        }),
        ('Guardian Information', {
            'fields': ('guardian_name', 'guardian_phone', 'guardian_email', 'guardian_relationship')
        }),
        ('Medical Information', {
            'fields': ('blood_group', 'medical_conditions')
        }),
    )


@admin.register(AcademicYearEnrollment)
class AcademicYearEnrollmentAdmin(BaseAdmin):
    list_display = ['student', 'academic_session', 'year_of_study', 'semester_number', 'status', 'enrollment_date']
    list_filter = ['academic_session', 'year_of_study', 'semester_number', 'status']
    search_fields = ['student__student_id', 'student__user__first_name', 'student__user__last_name']
    
    fieldsets = (
        ('Student & Session', {
            'fields': ('student', 'academic_session', 'semester')
        }),
        ('Year & Semester', {
            'fields': ('year_of_study', 'semester_number', 'status')
        }),
        ('Additional Info', {
            'fields': ('enrolled_by', 'remarks')
        }),
    )


@admin.register(Enrollment)
class EnrollmentAdmin(BaseAdmin):
    list_display = ['student', 'course', 'semester', 'academic_year_enrollment', 'is_active']
    list_filter = ['semester', 'is_active']


@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(BaseAdmin):
    list_display = ['first_name', 'last_name', 'programme_applied', 'status', 'application_date']
    list_filter = ['status', 'session']
    search_fields = ['first_name', 'last_name', 'email']
