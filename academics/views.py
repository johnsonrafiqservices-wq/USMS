from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.template.loader import render_to_string
from accounts.decorators import role_required
from .models import (
    Faculty, Department, Programme, Course, AcademicSession,
    CourseAllocation, Timetable, Attendance, StudentResult, GradeScale, Intake, Campus,
    StudyYear, StudySemester, StudyLevel
)
from .forms import (
    ProgrammeCourseForm, CourseForm, CourseAllocationForm, TimetableForm,
    DepartmentForm, ProgrammeForm, AcademicSessionForm, IntakeForm, FacultyForm, CampusForm, StudyLevelForm
)


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


@login_required
@role_required(['admin', 'registrar'])
def programme_edit(request, pk):
    programme = get_object_or_404(Programme, pk=pk)
    if request.method == 'POST':
        form = ProgrammeForm(request.POST, instance=programme)
        if form.is_valid():
            form.save()
            messages.success(request, 'Programme updated successfully.')
            return redirect('academics:programme_list')
    else:
        form = ProgrammeForm(instance=programme)
    
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
@role_required(['admin', 'registrar'])
def faculty_create(request):
    if request.method == 'POST':
        form = FacultyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Faculty created successfully.')
            return redirect('academics:department_list')
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
            return redirect('academics:department_list')
    else:
        form = FacultyForm(instance=faculty)
    
    return render(request, 'academics/faculty_form.html', {'form': form, 'title': 'Edit Faculty'})


@login_required
@role_required(['admin', 'registrar'])
def faculty_delete(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    if request.method == 'POST':
        faculty.delete()
        messages.success(request, 'Faculty deleted successfully.')
        return redirect('academics:department_list')
    
    return render(request, 'academics/confirm_delete.html', {'object': faculty, 'model_name': 'Faculty'})


# CRUD Views for Campuses
@login_required
@role_required(['admin', 'registrar'])
def campus_create(request):
    if request.method == 'POST':
        form = CampusForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campus created successfully.')
            return redirect('academics:department_list')
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
            return redirect('academics:department_list')
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
        return redirect('academics:department_list')
    
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
    
    form = CourseForm()
    programme_id = request.GET.get('programme_id')
    # If programme_id is provided, pre-select that programme
    if programme_id:
        try:
            programme = Programme.objects.get(pk=programme_id)
            form.fields['programmes'].initial = [programme.pk]
        except Programme.DoesNotExist:
            pass
    
    # Check if this is an AJAX request (simplified check)
    is_ajax = request.GET.get('ajax') == '1' or 'application/json' in request.headers.get('Accept', '')
    
    if is_ajax:
        html = render_to_string('academics/course_create_modal_form.html', {
            'form': form, 
            'programme_id': programme_id
        }, request=request)
        return JsonResponse({'html': html})
    
    # For non-AJAX requests, render the full page
    return render(request, 'academics/course_create_form.html', {
        'form': form, 
        'programme_id': programme_id
    })


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
    return render(request, 'academics/programme_list.html', {
        'programmes': programmes,
    })


@login_required
def department_list(request):
    departments = Department.objects.select_related('faculty').all()
    faculties = Faculty.objects.all()
    return render(request, 'academics/department_list.html', {
        'departments': departments,
        'faculties': faculties,
    })


@login_required
def department_detail(request, pk):
    department = get_object_or_404(Department, pk=pk)
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
    course = get_object_or_404(Course, pk=pk)
    allocations = CourseAllocation.objects.filter(course=course).select_related('lecturer', 'semester')
    return render(request, 'academics/course_detail.html', {
        'course': course,
        'allocations': allocations,
    })


@login_required
@role_required(['admin', 'registrar'])
def course_create(request):
    from django.http import JsonResponse
    if request.method == 'POST':
        from .forms import CourseForm
        form = CourseForm(request.POST)
        
        # Check if this is an edit request
        is_edit = 'edit' in request.path
        course_id = None
        
        if is_edit:
            # Extract course ID from URL
            path_parts = request.path.strip('/').split('/')
            if 'edit' in path_parts:
                edit_index = path_parts.index('edit')
                if edit_index > 0:
                    course_id = path_parts[edit_index - 1]
            
            if course_id:
                try:
                    course = Course.objects.get(pk=course_id)
                    form = CourseForm(request.POST, instance=course)
                except Course.DoesNotExist:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'message': 'Course not found.'})
                    messages.error(request, 'Course not found.')
                    return redirect('academics:course_list')
        
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
            else:
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
            
            # Clear existing programmes and add new ones for edit
            if course_id and is_edit:
                course.programme.clear()
            
            # Assign course to selected programmes with year/semester info
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
        from .forms import CourseForm
        form = CourseForm()
        
        # Check if this is an edit request and populate form
        if 'edit' in request.path:
            path_parts = request.path.strip('/').split('/')
            if 'edit' in path_parts:
                edit_index = path_parts.index('edit')
                if edit_index > 0:
                    course_id = path_parts[edit_index - 1]
                    try:
                        course = Course.objects.get(pk=course_id)
                        form = CourseForm(instance=course)
                        # Pre-populate department field
                        if course.programme.exists():
                            first_programme = course.programme.first()
                            form.initial['department'] = first_programme.department
                    except Course.DoesNotExist:
                        pass

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'academics/course_form_fragment.html', {'form': form, 'title': 'Create Course'})

    return render(request, 'academics/course_form.html', {'form': form, 'title': 'Create Course'})


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
