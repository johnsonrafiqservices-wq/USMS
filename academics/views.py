from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.template.loader import render_to_string
from django import forms
from django.apps import apps
from accounts.decorators import role_required, academic_read_required
from .models import (
    Faculty, Department, Programme, Course, AcademicSession,
    CourseAllocation, Timetable, Attendance, StudentResult, GradeScale, Intake, Campus,
    StudyYear, StudySemester, StudyLevel
)
from .forms import (
    ProgrammeCourseForm, CourseForm, CourseAllocationForm, TimetableForm,
    DepartmentForm, ProgrammeForm, AcademicSessionForm, IntakeForm, FacultyForm, CampusForm, StudyLevelForm
)
from students import models as students_models


# CRUD Views for Departments
@login_required
@role_required(['admin', 'registrar'])
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department created successfully.')
            return redirect('academics:department_list')
    else:
        form = DepartmentForm()
    
    return render(request, 'academics/department_form.html', {'form': form, 'title': 'Create Department'})


@login_required
@role_required(['admin', 'registrar'])
def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully.')
            return redirect('academics:department_list')
    else:
        form = DepartmentForm(instance=department)
    
    return render(request, 'academics/department_form.html', {'form': form, 'title': 'Edit Department'})


@login_required
@role_required(['admin', 'registrar'])
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department.delete()
        messages.success(request, 'Department deleted successfully.')
        return redirect('academics:department_list')
    
    return render(request, 'academics/confirm_delete.html', {'object': department, 'model_name': 'Department'})


# CRUD Views for Programmes
@login_required
def programme_detail(request, pk):
    programme = get_object_or_404(Programme, pk=pk)
    
    # Get students in this programme
    from students.models import Student
    students = Student.objects.filter(programme=programme).select_related('user', 'intake', 'current_year', 'current_semester_number')
    
    # Group students by study year
    students_by_year = {}
    for student in students:
        year_key = student.current_year.name if student.current_year else 'Unassigned'
        if year_key not in students_by_year:
            students_by_year[year_key] = []
        students_by_year[year_key].append(student)
    
    # Get current year students (active) - use the first year as current
    current_year = StudyYear.objects.first()
    current_year_students = students_by_year.get(current_year.name, []) if current_year else []
    
    # Get all study years for this programme
    programme_years = StudyYear.objects.all().order_by('level')
    
    # Get study semesters and intakes for filters
    study_semesters = StudySemester.objects.all().order_by('number')
    intakes = Intake.objects.all().order_by('-created_at')
    
    # Get programme statistics
    total_students = students.count()
    active_students = len(current_year_students)
    
    # Use all students for the filterable list
    all_students = list(students)
    
    return render(request, 'academics/programme_detail.html', {
        'programme': programme,
        'students_by_year': students_by_year,
        'current_year_students': all_students,  # All students for filtering
        'current_year': current_year,
        'programme_years': programme_years,
        'study_semesters': study_semesters,
        'intakes': intakes,
        'total_students': total_students,
        'active_students': active_students,
    })


@login_required
@role_required(['admin', 'registrar'])
def programme_create(request):
    if request.method == 'POST':
        form = ProgrammeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Programme created successfully.')
            return redirect('academics:programme_list')
    else:
        form = ProgrammeForm()
    
    return render(request, 'academics/programme_form.html', {'form': form, 'title': 'Create Programme'})


from django.http import JsonResponse
from django.template.loader import render_to_string

@login_required
@role_required(['admin', 'registrar'])
def programme_edit(request, pk):
    programme = get_object_or_404(Programme, pk=pk)
    if request.method == 'POST':
        form = ProgrammeForm(request.POST, instance=programme)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Programme updated successfully.'})
            messages.success(request, 'Programme updated successfully.')
            return redirect('academics:programme_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors.as_json()})
    else:
        form = ProgrammeForm(instance=programme)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('academics/programme_edit_modal.html', {'form': form, 'programme': programme}, request=request)
        return JsonResponse({'html': html})
    
    return render(request, 'academics/programme_form.html', {'form': form, 'title': 'Edit Programme'})


@login_required
@role_required(['admin', 'registrar'])
def programme_delete(request, pk):
    programme = get_object_or_404(Programme, pk=pk)
    if request.method == 'POST':
        programme.delete()
        messages.success(request, 'Programme deleted successfully.')
        return redirect('academics:programme_list')
    
    return render(request, 'academics/confirm_delete.html', {'object': programme, 'model_name': 'Programme'})


# CRUD Views for Academic Sessions
@login_required
@role_required(['admin', 'registrar'])
def session_create(request):
    if request.method == 'POST':
        form = AcademicSessionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Academic session created successfully.')
            return redirect('academics:session_list')
    else:
        form = AcademicSessionForm()
    
    return render(request, 'academics/session_form.html', {'form': form, 'title': 'Create Academic Session'})


@login_required
@role_required(['admin', 'registrar'])
def session_edit(request, pk):
    session = get_object_or_404(AcademicSession, pk=pk)
    if request.method == 'POST':
        form = AcademicSessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, 'Academic session updated successfully.')
            return redirect('academics:session_list')
    else:
        form = AcademicSessionForm(instance=session)
    
    return render(request, 'academics/session_form.html', {'form': form, 'title': 'Edit Academic Session'})


@login_required
@role_required(['admin', 'registrar'])
def session_delete(request, pk):
    session = get_object_or_404(AcademicSession, pk=pk)
    if request.method == 'POST':
        session.delete()
        messages.success(request, 'Academic session deleted successfully.')
        return redirect('academics:session_list')
    
    return render(request, 'academics/confirm_delete.html', {'object': session, 'model_name': 'Academic Session'})


# CRUD Views for Intakes
@login_required
@role_required(['admin', 'registrar'])
def intake_create(request):
    if request.method == 'POST':
        form = IntakeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Intake created successfully.')
            return redirect('academics:intake_list')
    else:
        form = IntakeForm()
    
    return render(request, 'academics/intake_form.html', {'form': form, 'title': 'Create Intake'})


@login_required
@role_required(['admin', 'registrar'])
def intake_edit(request, pk):
    intake = get_object_or_404(Intake, pk=pk)
    if request.method == 'POST':
        form = IntakeForm(request.POST, instance=intake)
        if form.is_valid():
            form.save()
            messages.success(request, 'Intake updated successfully.')
            return redirect('academics:intake_list')
    else:
        form = IntakeForm(instance=intake)
    
    return render(request, 'academics/intake_form.html', {'form': form, 'title': 'Edit Intake'})


@login_required
@role_required(['admin', 'registrar'])
def intake_delete(request, pk):
    intake = get_object_or_404(Intake, pk=pk)
    if request.method == 'POST':
        intake.delete()
        messages.success(request, 'Intake deleted successfully.')
        return redirect('academics:intake_list')
    
    return render(request, 'academics/confirm_delete.html', {'object': intake, 'model_name': 'Intake'})


# CRUD Views for Faculties
@login_required
def faculty_list(request):
    """List all faculties with statistics."""
    faculties = Faculty.objects.prefetch_related('departments', 'departments__programmes').all()
    campuses = Campus.objects.all()
    User = apps.get_model('accounts', 'User')
    deans = User.objects.filter(role=User.Role.FACULTY_DEAN)
    
    # Calculate stats for each faculty
    for faculty in faculties:
        faculty.programme_count = Programme.objects.filter(department__faculty=faculty).count()
        faculty.student_count = students_models.Student.objects.filter(programme__department__faculty=faculty).count()
    
    # Overall stats
    total_faculties = faculties.count()
    active_faculties = faculties.filter(is_active=True).count()
    total_departments = Department.objects.filter(faculty__in=faculties).count()
    total_programmes = Programme.objects.filter(department__faculty__in=faculties).count()
    
    context = {
        'faculties': faculties,
        'campuses': campuses,
        'deans': deans,
        'total_faculties': total_faculties,
        'active_faculties': active_faculties,
        'total_departments': total_departments,
        'total_programmes': total_programmes,
    }
    return render(request, 'academics/faculty_list.html', context)


@login_required
@role_required(['admin', 'registrar'])
def faculty_create(request):
    if request.method == 'POST':
        form = FacultyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Faculty created successfully.')
            return redirect('academics:faculty_list')
    else:
        form = FacultyForm()
    
    return render(request, 'academics/faculty_form.html', {'form': form, 'title': 'Create Faculty'})


@login_required
@role_required(['admin', 'registrar'])
def faculty_edit(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    if request.method == 'POST':
        form = FacultyForm(request.POST, instance=faculty)
        if form.is_valid():
            form.save()
            messages.success(request, 'Faculty updated successfully.')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Faculty updated successfully.'})
            return redirect('academics:faculty_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = FacultyForm(instance=faculty)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'academics/faculty_form_modal.html', {'form': form, 'faculty': faculty})
    
    return render(request, 'academics/faculty_form.html', {'form': form, 'title': 'Edit Faculty'})


@login_required
@role_required(['admin', 'registrar'])
def faculty_delete(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    if request.method == 'POST':
        faculty.delete()
        messages.success(request, 'Faculty deleted successfully.')
        return redirect('academics:faculty_list')
    
    return render(request, 'academics/confirm_delete.html', {'object': faculty, 'model_name': 'Faculty'})


@login_required
def faculty_detail(request, pk):
    """Faculty detail view showing departments, programmes, students, and courses."""
    faculty = get_object_or_404(Faculty.objects.prefetch_related('departments', 'departments__programmes'), pk=pk)
    
    # Get all departments in this faculty
    departments = faculty.departments.all()
    
    # Get all programmes in this faculty through departments (with courses)
    programmes = Programme.objects.filter(department__faculty=faculty).select_related('department', 'level').prefetch_related('courses')
    
    # Calculate programme stats
    for prog in programmes:
        prog.student_count = students_models.Student.objects.filter(programme=prog).count()
        prog.course_count = prog.courses.count()
    
    # Statistics
    total_departments = departments.count()
    total_programmes = programmes.count()
    
    # Student statistics - fetch actual students list with related data
    faculty_students = students_models.Student.objects.filter(
        programme__department__faculty=faculty
    ).select_related('programme', 'programme__department', 'intake', 'user').prefetch_related('year_enrollments__academic_session')
    
    total_students = faculty_students.count()
    
    # Student status counts
    student_status_counts = {}
    for status, _ in students_models.Student.Status.choices:
        student_status_counts[status] = students_models.Student.objects.filter(
            programme__department__faculty=faculty, status=status
        ).count()
    
    # Get intakes and sessions for filters (from academics models)
    intakes = Intake.objects.all().order_by('-created_at')
    academic_sessions = AcademicSession.objects.all().order_by('-name')
    
    # Get unique schedule options from programmes in this faculty
    schedule_options = programmes.values_list('schedule', flat=True).distinct()
    
    # Course statistics - fetch actual courses list with related data
    faculty_courses = Course.objects.filter(
        programme__department__faculty=faculty
    ).select_related('department').prefetch_related('programme', 'programme__department').distinct()
    total_courses = faculty_courses.count()
    core_courses = faculty_courses.filter(course_type='Core').count()
    elective_courses = faculty_courses.filter(course_type='Elective').count()
    
    # Get study years and semesters
    study_years = StudyYear.objects.all().order_by('level')
    study_semesters = StudySemester.objects.all().order_by('number')
    
    context = {
        'faculty': faculty,
        'departments': departments,
        'programmes': programmes,
        'total_departments': total_departments,
        'total_programmes': total_programmes,
        'faculty_students': faculty_students,
        'total_students': total_students,
        'student_status_counts': student_status_counts,
        'intakes': intakes,
        'academic_sessions': academic_sessions,
        'schedule_options': schedule_options,
        'faculty_courses': faculty_courses,
        'total_courses': total_courses,
        'core_courses': core_courses,
        'elective_courses': elective_courses,
        'study_years': study_years,
        'study_semesters': study_semesters,
    }
    return render(request, 'academics/faculty_detail.html', context)


# CRUD Views for Campuses
@login_required
def campus_list(request):
    """List all campuses with statistics."""
    campuses = Campus.objects.all().prefetch_related('faculties', 'faculties__departments')
    
    # Calculate stats for each campus
    for campus in campuses:
        campus.faculty_count = Faculty.objects.filter(campus=campus).count()
        campus.department_count = Department.objects.filter(faculty__campus=campus).count()
        campus.student_count = students_models.Student.objects.filter(programme__department__faculty__campus=campus).count()
    
    context = {
        'campuses': campuses,
        'total_campuses': campuses.count(),
        'active_campuses': campuses.filter(is_active=True).count(),
    }
    return render(request, 'academics/campus_list.html', context)


@login_required
@role_required(['admin', 'registrar'])
def campus_create(request):
    if request.method == 'POST':
        form = CampusForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campus created successfully.')
            return redirect('academics:campus_list')
    else:
        form = CampusForm()
    
    return render(request, 'academics/campus_form.html', {'form': form, 'title': 'Create Campus'})


@login_required
@role_required(['admin', 'registrar'])
def campus_edit(request, pk):
    campus = get_object_or_404(Campus, pk=pk)
    if request.method == 'POST':
        form = CampusForm(request.POST, instance=campus)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campus updated successfully.')
            return redirect('academics:campus_list')
    else:
        form = CampusForm(instance=campus)
    
    return render(request, 'academics/campus_form.html', {'form': form, 'title': 'Edit Campus'})


@login_required
@role_required(['admin', 'registrar'])
def campus_delete(request, pk):
    campus = get_object_or_404(Campus, pk=pk)
    if request.method == 'POST':
        campus.delete()
        messages.success(request, 'Campus deleted successfully.')
        return redirect('academics:campus_list')
    
    return render(request, 'academics/confirm_delete.html', {'object': campus, 'model_name': 'Campus'})


@login_required
@role_required(['admin', 'registrar'])
def course_create(request):
    from .forms import CourseForm
    
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            # The programmes are now handled by the form itself via the ManyToMany field
            # No need to manually add them here
            return JsonResponse({
                'success': True,
                'message': 'Course created successfully.'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors.as_json()
            })
    
    # For non-POST requests, redirect to course list where the modal is available
    return redirect('academics:course_list')


@login_required
@role_required(['admin', 'registrar'])
def course_remove(request, pk):
    course = get_object_or_404(Course, pk=pk)
    programme_id = request.POST.get('programme_id')
    
    if programme_id:
        programme = Programme.objects.get(pk=programme_id)
        programme.courses.remove(course)
        return JsonResponse({
            'success': True,
            'message': 'Course removed from programme successfully.'
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Programme ID is required.'
        })


@login_required
@role_required(['admin', 'registrar'])
def programme_courses(request, pk):
    programme = get_object_or_404(Programme, pk=pk)
    
    if request.method == 'POST':
        form = ProgrammeCourseForm(request.POST, instance=programme)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': 'Courses updated successfully.'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors.as_json()
            })
    
    # For GET requests, render the full page
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        from .forms import CourseForm
        course_form = CourseForm()
        # Pre-select current programme
        course_form.fields['programmes'].initial = [programme.pk]
        faculties = Faculty.objects.filter(is_active=True).prefetch_related('departments__programmes')
        study_years = StudyYear.objects.all()
        study_semesters = StudySemester.objects.all()
        all_courses = Course.objects.filter(is_active=True).select_related('department')
        return render(request, 'academics/programme_courses.html', {
            'programme': programme,
            'course_form': course_form,
            'faculties': faculties,
            'study_years': study_years,
            'study_semesters': study_semesters,
            'all_courses': all_courses,
        })
    
    # For AJAX requests, return form HTML
    form = ProgrammeCourseForm(instance=programme)
    html = render_to_string('academics/programme_courses_form.html', {'form': form, 'programme': programme}, request=request)
    return JsonResponse({'html': html})


# CRUD Views for Study Levels
@login_required
@role_required(['admin', 'registrar'])
def study_level_list(request):
    study_levels = StudyLevel.objects.all().order_by('level_number')
    return render(request, 'academics/study_level_list.html', {
        'study_levels': study_levels,
    })


@login_required
@role_required(['admin', 'registrar'])
def study_level_create(request):
    if request.method == 'POST':
        form = StudyLevelForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': 'Study level created successfully.'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors.as_json()
            })
    
    form = StudyLevelForm()
    return render(request, 'academics/study_level_form.html', {
        'form': form,
        'title': 'Add Study Level'
    })


@login_required
@role_required(['admin', 'registrar'])
def study_level_edit(request, pk):
    study_level = get_object_or_404(StudyLevel, pk=pk)
    
    if request.method == 'POST':
        form = StudyLevelForm(request.POST, instance=study_level)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': 'Study level updated successfully.'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors.as_json()
            })
    
    form = StudyLevelForm(instance=study_level)
    return render(request, 'academics/study_level_form.html', {
        'form': form,
        'title': 'Edit Study Level',
        'study_level': study_level
    })


@login_required
@role_required(['admin', 'registrar'])
def study_level_delete(request, pk):
    study_level = get_object_or_404(StudyLevel, pk=pk)
    
    if request.method == 'POST':
        # Check if study level is used by any programmes
        if study_level.programmes.exists():
            return JsonResponse({
                'success': False,
                'message': 'Cannot delete study level. It is associated with programmes.'
            })
        
        study_level.delete()
        return JsonResponse({
            'success': True,
            'message': 'Study level deleted successfully.'
        })
    
    return render(request, 'academics/study_level_delete.html', {
        'study_level': study_level
    })


@login_required
def programme_list(request):
    programmes = Programme.objects.select_related('department__faculty').all()
    if request.user.is_department_head:
        dept = Department.objects.filter(head_of_department=request.user).first()
        programmes = programmes.filter(department=dept) if dept else programmes.none()
    elif request.user.is_faculty_dean:
        programmes = programmes.filter(department__faculty__dean=request.user)
    faculties = Faculty.objects.filter(is_active=True).prefetch_related('departments')
    departments = Department.objects.select_related('faculty').all()
    User = apps.get_model('accounts', 'User')
    coordinators = User.objects.filter(role=User.Role.PROGRAMME_COORDINATOR)
    return render(request, 'academics/programme_list.html', {
        'programmes': programmes,
        'faculties': faculties,
        'departments': departments,
        'coordinators': coordinators,
    })


@login_required
def department_list(request):
    departments = Department.objects.select_related('faculty').all()
    if request.user.is_department_head:
        dept = Department.objects.filter(head_of_department=request.user).first()
        departments = departments.filter(pk=dept.pk) if dept else departments.none()
    elif request.user.is_faculty_dean:
        departments = departments.filter(faculty__dean=request.user)
    faculties = Faculty.objects.all()
    User = apps.get_model('accounts', 'User')
    heads = User.objects.filter(role=User.Role.DEPARTMENT_HEAD)
    return render(request, 'academics/department_list.html', {
        'departments': departments,
        'faculties': faculties,
        'heads': heads,
    })


@login_required
def department_detail(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.user.is_department_head and department.head_of_department != request.user:
        messages.error(request, 'You do not have permission to view this department.')
        return redirect('accounts:dashboard')
    if request.user.is_faculty_dean and department.faculty.dean != request.user:
        messages.error(request, 'You do not have permission to view this department.')
        return redirect('accounts:dashboard')
    courses = Course.objects.filter(department=department)
    programmes = Programme.objects.filter(department=department)
    return render(request, 'academics/department_detail.html', {
        'department': department,
        'courses': courses,
        'programmes': programmes,
    })


@login_required
def course_list(request):
    courses = Course.objects.select_related('department').all()
    if request.user.is_department_head:
        dept = Department.objects.filter(head_of_department=request.user).first()
        courses = courses.filter(department=dept) if dept else courses.none()
    elif request.user.is_faculty_dean:
        courses = courses.filter(department__faculty__dean=request.user)
    department_filter = request.GET.get('department')
    level_filter = request.GET.get('level')
    if department_filter:
        courses = courses.filter(department_id=department_filter)
    if level_filter:
        courses = courses.filter(level=level_filter)
    departments = Department.objects.all()
    
    from .forms import CourseForm
    course_form = CourseForm()
    
    faculties = Faculty.objects.filter(is_active=True).prefetch_related('departments__programmes')
    study_years = StudyYear.objects.all()
    study_semesters = StudySemester.objects.all()
    
    return render(request, 'academics/course_list.html', {
        'courses': courses,
        'departments': departments,
        'course_form': course_form,
        'faculties': faculties,
        'study_years': study_years,
        'study_semesters': study_semesters,
    })


@login_required
def course_detail(request, pk):
    course = get_object_or_404(
        Course.objects.select_related('department').prefetch_related('programme', 'programme__department'),
        pk=pk
    )
    if request.user.is_department_head and course.department.head_of_department != request.user:
        messages.error(request, 'You do not have permission to view this course.')
        return redirect('accounts:dashboard')
    if request.user.is_faculty_dean and course.department.faculty.dean != request.user:
        messages.error(request, 'You do not have permission to view this course.')
        return redirect('accounts:dashboard')
    allocations = CourseAllocation.objects.filter(course=course).select_related('lecturer', 'semester')
    total_allocations = allocations.count()
    active_allocations = allocations.filter(is_active=True).count()
    past_allocations = total_allocations - active_allocations
    programmes = course.programme.all()
    total_programmes = programmes.count()

    return render(request, 'academics/course_detail.html', {
        'course': course,
        'allocations': allocations,
        'programmes': programmes,
        'total_programmes': total_programmes,
        'total_allocations': total_allocations,
        'active_allocations': active_allocations,
        'past_allocations': past_allocations,
    })


@login_required
@role_required(['admin', 'registrar'])
def course_allocation_popup(request, pk):
    course = get_object_or_404(Course.objects.select_related('department'), pk=pk)
    allocations = CourseAllocation.objects.filter(course=course).select_related('lecturer', 'semester')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete':
            allocation_id = request.POST.get('allocation_id')
            allocation = get_object_or_404(CourseAllocation, pk=allocation_id, course=course)
            allocation.delete()
            return JsonResponse({'success': True, 'message': 'Allocation removed successfully.'})

        data = request.POST.copy()
        data['course'] = course.pk
        form = CourseAllocationForm(data)
        if form.is_valid():
            allocation = form.save(commit=False)
            allocation.course = course
            allocation.is_active = True
            allocation.save()
            return JsonResponse({'success': True, 'message': 'Allocation saved successfully.'})
        return JsonResponse({'success': False, 'errors': form.errors})

    form = CourseAllocationForm(initial={'course': course})
    form.fields['course'].queryset = Course.objects.filter(pk=course.pk)
    form.fields['course'].widget = forms.HiddenInput()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'academics/course_allocation_fragment.html', {
            'course': course,
            'allocations': allocations,
            'form': form,
        })

    return redirect('academics:course_detail', pk=course.pk)


@login_required
@role_required(['admin', 'registrar'])
def course_create(request, pk=None):
    from django.http import JsonResponse
    from .forms import CourseForm

    is_edit = pk is not None
    course = None

    if is_edit:
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Course not found.'})
            messages.error(request, 'Course not found.')
            return redirect('academics:course_list')

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course if is_edit else None)

        # Extract programme information
        programmes = request.POST.getlist('programmes')
        programme_years = {}
        programme_semesters = {}
        programme_course_types = {}

        for prog_id in programmes:
            programme_years[prog_id] = request.POST.get(f'programme_year_{prog_id}')
            programme_semesters[prog_id] = request.POST.get(f'programme_semester_{prog_id}')
            programme_course_types[prog_id] = request.POST.get(f'programme_course_type_{prog_id}')

        # Check if at least one programme is selected with complete information
        valid_programmes = []
        for prog_id in programmes:
            if programme_years.get(prog_id) and programme_semesters.get(prog_id) and programme_course_types.get(prog_id):
                valid_programmes.append(prog_id)

        if not valid_programmes:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Please select at least one programme with complete year, semester, and course type information.'
                })
            messages.error(request, 'Please select at least one programme with complete information.')
            return redirect('academics:course_list')

        # Get first programme for department and level info
        first_programme = Programme.objects.get(pk=valid_programmes[0])
        first_study_year = StudyYear.objects.get(pk=programme_years[valid_programmes[0]])

        # Set derived fields
        form.data = form.data.copy()
        form.data['department'] = first_programme.department.pk
        form.data['level'] = first_study_year.level * 100  # Convert to course level (100, 200, 300, etc.)
        form.data['course_type'] = programme_course_types[valid_programmes[0]]

        if form.is_valid():
            course = form.save()

            if is_edit:
                course.programme.clear()

            # Assign course to selected programmes
            for prog_id in valid_programmes:
                programme = Programme.objects.get(pk=prog_id)
                course.programme.add(programme)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Course {"updated" if is_edit else "created"} successfully.',
                    'redirect': '/academics/courses/'
                })
            messages.success(request, f'Course {"updated" if is_edit else "created"} successfully.')
            return redirect('academics:course_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': str(form.errors)
                })
    else:
        form = CourseForm(instance=course if is_edit else None)
        if is_edit and course and course.programme.exists():
            first_programme = course.programme.first()
            form.initial['department'] = first_programme.department

    study_years = StudyYear.objects.all()
    study_semesters = StudySemester.objects.all()
    faculties = Faculty.objects.filter(is_active=True).prefetch_related('departments__programmes')
    selected_programme_ids = []
    if is_edit and course:
        selected_programme_ids = list(course.programme.values_list('pk', flat=True))

    title_text = 'Edit Course' if is_edit else 'Create Course'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'academics/course_form_fragment.html', {
            'form': form,
            'title': title_text,
            'study_years': study_years,
            'study_semesters': study_semesters,
            'faculties': faculties,
            'selected_programme_ids': selected_programme_ids,
        })

    return render(request, 'academics/course_form.html', {'form': form, 'title': title_text})


@login_required
@role_required(['admin', 'registrar'])
def add_existing_course_to_programme(request):
    from django.http import JsonResponse
    if request.method == 'POST':
        programme_id = request.POST.get('programme_id')
        course_id = request.POST.get('course_id')
        year_id = request.POST.get('year_id')
        semester_id = request.POST.get('semester_id')
        course_type = request.POST.get('course_type')
        
        if not all([programme_id, course_id, year_id, semester_id, course_type]):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Please provide all required information.'
                })
            messages.error(request, 'Please provide all required information.')
            return redirect('academics:programme_list')
        
        try:
            programme = Programme.objects.get(pk=programme_id)
            course = Course.objects.get(pk=course_id)
            study_year = StudyYear.objects.get(pk=year_id)
            study_semester = StudySemester.objects.get(pk=semester_id)
            
            # Add course to programme
            course.programme.add(programme)
            
            # Note: CourseAllocation requires a lecturer, so we'll skip automatic allocation
            # Lecturer assignment can be done separately through the allocation management
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Course "{course.title}" has been added to "{programme.name}" for {study_year.name} - {study_semester.name}.',
                    'redirect': '/academics/programmes/'
                })
            
            messages.success(request, f'Course "{course.title}" has been added to "{programme.name}" for {study_year.name} - {study_semester.name}.')
            return redirect('academics:programme_list')
            
        except (Programme.DoesNotExist, Course.DoesNotExist, StudyYear.DoesNotExist, StudySemester.DoesNotExist) as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                })
            messages.error(request, str(e))
            return redirect('academics:programme_list')
    
    # GET request - show form to add existing course
    programmes = Programme.objects.filter(is_active=True)
    courses = Course.objects.filter(is_active=True).select_related('department')
    study_years = StudyYear.objects.all()
    study_semesters = StudySemester.objects.all()
    
    return render(request, 'academics/add_existing_course.html', {
        'programmes': programmes,
        'courses': courses,
        'study_years': study_years,
        'study_semesters': study_semesters,
    })


@login_required
@role_required(['admin', 'lecturer'])
def grade_management(request):
    user = request.user
    if user.is_admin or user.is_superuser:
        allocations = CourseAllocation.objects.all().select_related('course', 'lecturer', 'semester')
    else:
        from staff.models import StaffProfile
        try:
            staff = StaffProfile.objects.get(user=user)
            allocations = CourseAllocation.objects.filter(
                lecturer=staff
            ).select_related('course', 'semester')
        except StaffProfile.DoesNotExist:
            allocations = CourseAllocation.objects.none()
    return render(request, 'academics/grade_management.html', {'allocations': allocations})


@login_required
@role_required(['admin', 'lecturer'])
def enter_results(request, allocation_id):
    allocation = get_object_or_404(CourseAllocation, pk=allocation_id)
    from students.models import Enrollment
    enrollments = Enrollment.objects.filter(
        course=allocation.course,
        semester=allocation.semester,
        is_active=True
    ).select_related('student')

    if request.method == 'POST':
        for enrollment in enrollments:
            ca = request.POST.get(f'ca_{enrollment.student.id}', 0)
            exam = request.POST.get(f'exam_{enrollment.student.id}', 0)
            result, created = StudentResult.objects.get_or_create(
                student=enrollment.student,
                course_allocation=allocation,
                defaults={'recorded_by': request.user}
            )
            result.ca_score = float(ca)
            result.exam_score = float(exam)
            result.calculate_grade()
        messages.success(request, 'Results saved successfully.')
        return redirect('academics:grade_management')

    existing_results = {
        r.student_id: r for r in StudentResult.objects.filter(course_allocation=allocation)
    }
    return render(request, 'academics/enter_results.html', {
        'allocation': allocation,
        'enrollments': enrollments,
        'existing_results': existing_results,
    })


@login_required
def attendance_list(request):
    user = request.user
    if user.role == 'lecturer':
        from staff.models import StaffProfile
        try:
            staff = StaffProfile.objects.get(user=user)
            allocations = CourseAllocation.objects.filter(
                lecturer=staff
            )
        except StaffProfile.DoesNotExist:
            allocations = CourseAllocation.objects.none()
    else:
        allocations = CourseAllocation.objects.all()
    return render(request, 'academics/attendance_list.html', {'allocations': allocations})


@login_required
@role_required(['admin', 'lecturer'])
def take_attendance(request, allocation_id):
    from students.models import Enrollment
    from django.utils import timezone

    allocation = get_object_or_404(CourseAllocation, pk=allocation_id)
    enrollments = Enrollment.objects.filter(
        course=allocation.course,
        semester=allocation.semester,
        is_active=True
    ).select_related('student')

    if request.method == 'POST':
        date = request.POST.get('date', timezone.now().date())
        for enrollment in enrollments:
            is_present = request.POST.get(f'present_{enrollment.student.id}') == 'on'
            Attendance.objects.update_or_create(
                student=enrollment.student,
                course_allocation=allocation,
                date=date,
                defaults={
                    'is_present': is_present,
                    'recorded_by': request.user,
                }
            )
        messages.success(request, 'Attendance recorded successfully.')
        return redirect('academics:attendance_list')

    return render(request, 'academics/take_attendance.html', {
        'allocation': allocation,
        'enrollments': enrollments,
    })


@login_required
def my_timetable(request):
    user = request.user
    if user.is_student:
        from students.models import Student, Enrollment
        try:
            student = Student.objects.get(user=user)
            enrollments = Enrollment.objects.filter(
                student=student, is_active=True
            )
            course_ids = enrollments.values_list('course_id', flat=True)
            timetable = Timetable.objects.filter(
                course_allocation__course_id__in=course_ids
            ).select_related('course_allocation__course')
        except Exception:
            timetable = Timetable.objects.none()
    elif user.role == 'lecturer':
        from staff.models import StaffProfile
        try:
            staff = StaffProfile.objects.get(user=user)
            timetable = Timetable.objects.filter(
                course_allocation__lecturer=staff
            ).select_related('course_allocation__course')
        except Exception:
            timetable = Timetable.objects.none()
    else:
        timetable = Timetable.objects.all().select_related('course_allocation__course')

    return render(request, 'academics/timetable.html', {'timetable': timetable})


# ── Academic Sessions (Years) ──────────────────────────────────────

@login_required
@role_required(['admin', 'registrar'])
def session_list(request):
    sessions = AcademicSession.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        is_current = request.POST.get('is_current') == 'on'
        if name:
            if AcademicSession.objects.filter(name=name).exists():
                messages.error(request, f'Academic Year "{name}" already exists.')
            else:
                AcademicSession.objects.create(name=name, is_current=is_current)
                messages.success(request, f'Academic Year "{name}" created.')
                return redirect('academics:session_list')
        else:
            messages.error(request, 'Please provide a name for the academic year.')
    return render(request, 'academics/session_list.html', {'sessions': sessions})


@login_required
@role_required(['admin', 'registrar'])
def session_set_current(request, pk):
    session = get_object_or_404(AcademicSession, pk=pk)
    AcademicSession.objects.filter(is_current=True).update(is_current=False)
    session.is_current = True
    session.save(update_fields=['is_current'])
    messages.success(request, f'"{session.name}" is now the current academic year.')
    return redirect('academics:session_list')


# ── Intakes ────────────────────────────────────────────────────────

@login_required
@role_required(['admin', 'registrar'])
def intake_list(request):
    intakes = Intake.objects.prefetch_related('students').all()

    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        name = request.POST.get('name', '').strip()

        if not code or not name:
            messages.error(request, 'Code and Name are required.')
        elif Intake.objects.filter(code=code).exists():
            messages.error(request, f'An intake with code "{code}" already exists.')
        else:
            intake = Intake.objects.create(code=code, name=name)
            messages.success(request, f'Intake "{intake}" created.')
            return redirect('academics:intake_list')

    return render(request, 'academics/intake_list.html', {'intakes': intakes})


@login_required
@role_required(['admin', 'registrar'])
def intake_detail(request, pk):
    intake = get_object_or_404(
        Intake.objects.prefetch_related('students__user', 'students__programme'),
        pk=pk
    )
    students = intake.students.select_related('user', 'programme').all()
    return render(request, 'academics/intake_detail.html', {
        'intake': intake,
        'students': students,
    })
