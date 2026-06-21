from django import forms
from django.contrib.auth import get_user_model
from .models import Course, Department, Programme, CourseAllocation, Timetable, Faculty, Campus, AcademicSession, Intake, StudyLevel

User = get_user_model()


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'faculty', 'head_of_department', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'faculty': forms.Select(attrs={'class': 'form-select'}),
            'head_of_department': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['head_of_department'].queryset = User.objects.filter(
            role__in=[User.Role.DEPARTMENT_HEAD, User.Role.ADMIN, User.Role.REGISTRAR]
        ).order_by('first_name', 'last_name')


class StudyLevelForm(forms.ModelForm):
    class Meta:
        model = StudyLevel
        fields = ['name', 'code', 'level_number', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'level_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProgrammeForm(forms.ModelForm):
    class Meta:
        model = Programme
        fields = ['name', 'code', 'department', 'coordinator', 'level', 'schedule', 'duration_years', 
                  'total_credits', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'coordinator': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'schedule': forms.Select(attrs={'class': 'form-select'}),
            'duration_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_credits': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['coordinator'].queryset = User.objects.filter(
            role__in=[User.Role.PROGRAMME_COORDINATOR, User.Role.ADMIN, User.Role.REGISTRAR]
        ).order_by('first_name', 'last_name')


class AcademicSessionForm(forms.ModelForm):
    class Meta:
        model = AcademicSession
        fields = ['name', 'is_current']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class IntakeForm(forms.ModelForm):
    class Meta:
        model = Intake
        fields = ['code', 'name']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ['name', 'code', 'campus', 'dean', 'description', 'established_date', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'campus': forms.Select(attrs={'class': 'form-select'}),
            'dean': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'established_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dean'].queryset = User.objects.filter(
            role__in=[User.Role.FACULTY_DEAN, User.Role.ADMIN, User.Role.REGISTRAR]
        ).order_by('first_name', 'last_name')


class CampusForm(forms.ModelForm):
    class Meta:
        model = Campus
        fields = ['name', 'code', 'location', 'address', 'phone', 'email', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class ProgrammeCourseForm(forms.ModelForm):
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'form-check-input'}
        ),
        required=False
    )
    
    class Meta:
        model = Programme
        fields = ['courses']
        widgets = {
            'courses': forms.CheckboxSelectMultiple(
                attrs={'class': 'form-check-input'}
            ),
        }


class CourseForm(forms.ModelForm):
    programmes = forms.ModelMultipleChoiceField(
        queryset=Programme.objects.all(),
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'form-check-input'}
        ),
        required=False,
        help_text="Select all programmes this course will be available for"
    )
    
    class Meta:
        model = Course
        fields = ['code', 'title', 'department', 'programmes', 'credit_units', 'course_type',
                  'level', 'semester', 'description', 'max_students', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'credit_units': forms.NumberInput(attrs={'class': 'form-control'}),
            'course_type': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.NumberInput(attrs={'class': 'form-control'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'max_students': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class CourseAllocationForm(forms.ModelForm):
    class Meta:
        model = CourseAllocation
        fields = ['course', 'lecturer', 'semester']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'lecturer': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
        }


class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ['course_allocation', 'day', 'start_time', 'end_time', 'room', 'building']
        widgets = {
            'course_allocation': forms.Select(attrs={'class': 'form-select'}),
            'day': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'room': forms.TextInput(attrs={'class': 'form-control'}),
            'building': forms.TextInput(attrs={'class': 'form-control'}),
        }
