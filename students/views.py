from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from accounts.decorators import role_required
from .models import Student, Enrollment, AdmissionApplication
from .forms import StudentEditForm
from django.http import JsonResponse
from django.template.loader import render_to_string


@login_required
@role_required(['admin', 'registrar'])
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        form = StudentEditForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': 'Student information updated successfully.'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors.as_json()
            })
    
    form = StudentEditForm(instance=student)
    html = render_to_string('students/student_edit_form.html', {'form': form, 'student': student}, request=request)
    return JsonResponse({'html': html})


@login_required
@role_required(['admin', 'registrar'])
def student_list(request):
    students = Student.objects.select_related('user', 'programme').all()
    search = request.GET.get('search')
    status_filter = request.GET.get('status')
    level_filter = request.GET.get('level')

    if search:
        students = students.filter(
            Q(student_id__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search)
        )
    if status_filter:
        students = students.filter(status=status_filter)
    if level_filter:
        students = students.filter(current_year=level_filter)

    return render(request, 'students/student_list.html', {
        'students': students,
        'statuses': Student.Status.choices,
    })


@login_required
def student_detail(request, pk):
    student = get_object_or_404(
        Student.objects.select_related('user', 'programme__department__faculty'),
        pk=pk
    )

    # Only admin/registrar can view any student; students can only view themselves
    if request.user.role not in ('admin', 'registrar') and not request.user.is_superuser:
        try:
            own = Student.objects.get(user=request.user)
            if own.pk != student.pk:
                messages.error(request, 'You do not have permission to view this profile.')
                return redirect('accounts:dashboard')
        except Student.DoesNotExist:
            messages.error(request, 'Student profile not found.')
            return redirect('accounts:dashboard')

    from academics.models import StudentResult, Attendance
    from students.models import AcademicYearEnrollment
    from staff.models import Document

    enrollments = (
        Enrollment.objects
        .filter(student=student)
        .select_related('course', 'semester')
        .order_by('-semester__id')
    )
    results = (
        StudentResult.objects
        .filter(student=student)
        .select_related('course_allocation__course', 'course_allocation__semester')
        .order_by('-course_allocation__semester__id')
    )
    year_enrollments = (
        AcademicYearEnrollment.objects
        .filter(student=student)
        .select_related('academic_session', 'semester')
        .order_by('-academic_session__name', 'year_of_study', 'semester_number')
    )
    attendance = (
        Attendance.objects
        .filter(student=student)
        .select_related('course_allocation__course')
        .order_by('-date')[:50]
    )
    documents = (
        Document.objects
        .filter(student=student)
        .order_by('-uploaded_at')
    )

    # Finance
    try:
        from finance.models import Invoice, Payment
        invoices = Invoice.objects.filter(student=student).select_related('session').order_by('-issued_date')
        payments = Payment.objects.filter(invoice__student=student).order_by('-payment_date')[:10]
        total_billed = sum(inv.total_amount for inv in invoices)
        total_paid = sum(inv.amount_paid for inv in invoices)
        total_balance = sum(inv.balance for inv in invoices)
    except Exception:
        invoices, payments = [], []
        total_billed = total_paid = total_balance = 0

    cgpa = student.calculate_cgpa()
    graduation = student.check_graduation_eligibility()

    return render(request, 'students/student_detail.html', {
        'student': student,
        'enrollments': enrollments,
        'results': results,
        'year_enrollments': year_enrollments,
        'attendance': attendance,
        'documents': documents,
        'invoices': invoices,
        'payments': payments,
        'total_billed': total_billed,
        'total_paid': total_paid,
        'total_balance': total_balance,
        'cgpa': cgpa,
        'graduation': graduation,
        'active_tab': request.GET.get('tab', 'overview'),
    })


@login_required
def my_courses(request):
    """Student's enrolled courses view."""
    try:
        student = Student.objects.get(user=request.user)
        enrollments = Enrollment.objects.filter(
            student=student
        ).select_related('course', 'semester')
        current_semester = student.current_semester_number
        current_enrollments = enrollments.filter(semester=current_semester) if current_semester else enrollments
    except Student.DoesNotExist:
        student = None
        enrollments = Enrollment.objects.none()
        current_enrollments = Enrollment.objects.none()
        current_semester = None

    return render(request, 'students/my_courses.html', {
        'student': student,
        'enrollments': enrollments,
        'current_enrollments': current_enrollments,
        'current_semester': current_semester,
    })


@login_required
def my_results(request):
    """Student's academic results and transcript."""
    try:
        student = Student.objects.get(user=request.user)
        from academics.models import StudentResult
        results = StudentResult.objects.filter(
            student=student, is_published=True
        ).select_related('course_allocation__course', 'course_allocation__semester')
        cgpa = student.calculate_cgpa()
    except Student.DoesNotExist:
        student = None
        results = []
        cgpa = 0

    return render(request, 'students/my_results.html', {
        'student': student,
        'results': results,
        'cgpa': cgpa,
    })


@login_required
def course_registration(request):
    """Course registration for students."""
    from django.http import JsonResponse
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Student profile not found.'})
        messages.error(request, 'Student profile not found.')
        return redirect('accounts:dashboard')

    from academics.models import Course, StudySemester, StudentResult
    current_semester = student.current_semester_number

    available_courses = Course.objects.filter(
        programme__in=[student.programme],
        is_active=True
    ) if student.programme else Course.objects.none()
    enrolled_ids = Enrollment.objects.filter(
        student=student, semester=current_semester
    ).values_list('course_id', flat=True) if current_semester else []
    
    # Find courses the student has failed (grade_point < 1.0) - eligible for retake
    failed_course_ids = StudentResult.objects.filter(
        student=student, is_published=True, grade_point__lt=1.0
    ).values_list('course_allocation__course_id', flat=True)

    if request.method == 'POST':
        course_ids = request.POST.getlist('courses')
        retake_ids = request.POST.getlist('retakes')
        sem_id = request.POST.get('semester')
        if not sem_id:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Please select a semester.'})
            messages.error(request, 'Please select a semester.')
        else:
            sem = get_object_or_404(StudySemester, pk=sem_id)
            for course_id in course_ids:
                is_retake = str(course_id) in retake_ids
                Enrollment.objects.get_or_create(
                    student=student,
                    course_id=course_id,
                    semester=sem,
                    defaults={'is_retake': is_retake}
                )
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'{len(course_ids)} course(s) registered successfully.',
                    'redirect': '/students/my-courses/'
                })
            messages.success(request, f'{len(course_ids)} course(s) registered successfully.')
            return redirect('students:my_courses')

    semesters = StudySemester.objects.all()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'students/course_registration_fragment.html', {
            'student': student,
            'available_courses': available_courses,
            'enrolled_ids': list(enrolled_ids),
            'failed_course_ids': list(failed_course_ids),
            'semester': current_semester,
            'semesters': semesters,
        })

    return render(request, 'students/course_registration.html', {
        'student': student,
        'available_courses': available_courses,
        'enrolled_ids': list(enrolled_ids),
        'failed_course_ids': list(failed_course_ids),
        'semester': current_semester,
        'semesters': semesters,
    })


@login_required
@role_required(['admin', 'registrar'])
def admission_list(request):
    applications = AdmissionApplication.objects.all()
    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)
    return render(request, 'students/admission_list.html', {
        'applications': applications,
        'statuses': AdmissionApplication.Status.choices,
    })


@login_required
@role_required(['admin', 'registrar'])
def admission_review(request, pk):
    application = get_object_or_404(AdmissionApplication, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            application.status = AdmissionApplication.Status.ACCEPTED
            application.reviewed_by = request.user
            application.save()
            messages.success(request, 'Application accepted.')
        elif action == 'reject':
            application.status = AdmissionApplication.Status.REJECTED
            application.remarks = request.POST.get('remarks', '')
            application.reviewed_by = request.user
            application.save()
            messages.info(request, 'Application rejected.')
        return redirect('students:admission_list')

    return render(request, 'students/admission_review.html', {'application': application})


from django.contrib.auth import get_user_model
from academics.models import Programme, StudyYear, StudySemester, Intake

User = get_user_model()


@login_required
@role_required(['admin', 'registrar'])
def student_create(request):
    """Create a new student with user account."""
    programmes = Programme.objects.filter(is_active=True)
    study_years = StudyYear.objects.all()
    study_semesters = StudySemester.objects.all()
    intakes = Intake.objects.all()

    if request.method == 'POST':
        # User fields
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        # Student fields
        student_id = request.POST.get('student_id')
        programme_id = request.POST.get('programme')
        current_year_id = request.POST.get('current_year')
        current_semester_id = request.POST.get('current_semester')
        intake_id = request.POST.get('intake')
        status = request.POST.get('status', 'active')

        errors = {}

        # Validation
        if not first_name:
            errors['first_name'] = ['First name is required.']
        if not last_name:
            errors['last_name'] = ['Last name is required.']
        if not email:
            errors['email'] = ['Email is required.']
        if not student_id:
            errors['student_id'] = ['Student ID is required.']
        elif Student.objects.filter(student_id=student_id).exists():
            errors['student_id'] = ['Student ID already exists.']

        if User.objects.filter(email=email).exists():
            errors['email'] = ['Email already registered.']

        if errors:
            return JsonResponse({'success': False, 'errors': errors})

        try:
            # Create user
            username = email.split('@')[0] + str(User.objects.count() + 1)
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role='student',
                password=student_id  # Use student ID as initial password
            )

            # Create student profile
            student = Student.objects.create(
                user=user,
                student_id=student_id,
                programme_id=programme_id or None,
                current_year_id=current_year_id or None,
                current_semester_number_id=current_semester_id or None,
                intake_id=intake_id or None,
                status=status
            )

            return JsonResponse({
                'success': True,
                'message': f'Student {student_id} created successfully.',
                'student_id': student.id
            })

        except Exception as e:
            return JsonResponse({'success': False, 'errors': {'__all__': [str(e)]}})

    context = {
        'programmes': programmes,
        'study_years': study_years,
        'study_semesters': study_semesters,
        'intakes': intakes,
    }
    return render(request, 'students/student_create.html', context)
