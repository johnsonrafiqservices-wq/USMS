from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum
from .forms import CustomLoginForm, UserRegistrationForm, UserProfileForm
from .models import User
from .decorators import role_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


@login_required
def dashboard_view(request):
    user = request.user
    context = {'user': user}

    if user.is_admin or user.is_superuser:
        context.update(_get_admin_dashboard_context())
    elif user.is_student:
        context.update(_get_student_dashboard_context(user))
    elif user.is_lecturer:
        context.update(_get_lecturer_dashboard_context(user))
    elif user.is_finance_staff:
        context.update(_get_finance_dashboard_context())
    elif user.is_registrar:
        context.update(_get_registrar_dashboard_context())
    elif user.is_librarian:
        context.update(_get_librarian_dashboard_context())
    elif user.role == 'hostel_manager':
        context.update(_get_hostel_dashboard_context())

    return render(request, 'accounts/dashboard.html', context)


def _get_admin_dashboard_context():
    from students.models import Student, AdmissionApplication
    from academics.models import Course, Department, AcademicSession, Faculty
    from staff.models import StaffProfile
    from finance.models import Payment, Invoice
    try:
        total_students = Student.objects.filter(status='active').count()
        total_courses = Course.objects.filter(is_active=True).count()
        total_departments = Department.objects.count()
        total_staff = StaffProfile.objects.count()
        total_faculties = Faculty.objects.count()
        pending_admissions = AdmissionApplication.objects.filter(status='pending').count()
        current_session = AcademicSession.objects.filter(is_current=True).first()
        total_revenue = Payment.objects.filter(status='completed').aggregate(
            total=Sum('amount'))['total'] or 0
        pending_invoices = Invoice.objects.filter(status='pending').count()
        recent_students = Student.objects.select_related('user', 'programme').order_by('-id')[:5]
    except Exception:
        total_students = total_courses = total_departments = total_staff = 0
        total_faculties = pending_admissions = pending_invoices = 0
        total_revenue = 0
        current_session = None
        recent_students = []
    return {
        'dashboard_type': 'admin',
        'total_students': total_students,
        'total_courses': total_courses,
        'total_departments': total_departments,
        'total_staff': total_staff,
        'total_faculties': total_faculties,
        'pending_admissions': pending_admissions,
        'current_session': current_session,
        'total_revenue': total_revenue,
        'pending_invoices': pending_invoices,
        'recent_students': recent_students,
    }


def _get_student_dashboard_context(user):
    try:
        from students.models import Student, Enrollment
        from academics.models import StudentResult
        from finance.models import Invoice
        student = Student.objects.select_related('programme', 'current_year', 'current_semester_number').get(user=user)
        enrollments = Enrollment.objects.filter(student=student, is_active=True).select_related('course', 'semester')
        recent_results = StudentResult.objects.filter(
            student=student, is_published=True
        ).select_related('course_allocation__course').order_by('-id')[:5]
        total_owed = Invoice.objects.filter(student=student).aggregate(
            total=Sum('balance'))['total'] or 0
        cgpa = student.calculate_cgpa()
        return {
            'dashboard_type': 'student',
            'student': student,
            'enrollments': enrollments[:6],
            'enrollment_count': enrollments.count(),
            'recent_results': recent_results,
            'total_owed': total_owed,
            'cgpa': cgpa,
        }
    except Exception:
        return {'dashboard_type': 'student'}


def _get_lecturer_dashboard_context(user):
    try:
        from staff.models import StaffProfile
        from academics.models import CourseAllocation, Attendance
        from students.models import Enrollment
        staff = StaffProfile.objects.select_related('department').get(user=user)
        allocations = CourseAllocation.objects.filter(
            lecturer=staff, is_active=True
        ).select_related('course', 'semester')
        total_students = Enrollment.objects.filter(
            course__in=allocations.values('course'), is_active=True
        ).values('student').distinct().count()
        pending_attendance = Attendance.objects.filter(
            course_allocation__lecturer=staff
        ).count()
        return {
            'dashboard_type': 'lecturer',
            'staff': staff,
            'allocations': allocations,
            'course_count': allocations.count(),
            'total_students': total_students,
            'pending_attendance': pending_attendance,
        }
    except Exception:
        return {'dashboard_type': 'lecturer'}


def _get_finance_dashboard_context():
    try:
        from finance.models import Payment, Invoice, Scholarship
        total_revenue = Payment.objects.filter(status='completed').aggregate(
            total=Sum('amount'))['total'] or 0
        pending_invoices = Invoice.objects.filter(status='pending').count()
        overdue_invoices = Invoice.objects.filter(status='overdue').count()
        total_outstanding = Invoice.objects.filter(
            status__in=['pending', 'partial', 'overdue']
        ).aggregate(total=Sum('balance'))['total'] or 0
        recent_payments = Payment.objects.filter(
            status='completed'
        ).select_related('student__user').order_by('-payment_date')[:5]
        return {
            'dashboard_type': 'finance',
            'total_revenue': total_revenue,
            'pending_invoices': pending_invoices,
            'overdue_invoices': overdue_invoices,
            'total_outstanding': total_outstanding,
            'recent_payments': recent_payments,
        }
    except Exception:
        return {'dashboard_type': 'finance'}


def _get_registrar_dashboard_context():
    try:
        from students.models import Student, AdmissionApplication, AcademicYearEnrollment
        from academics.models import AcademicSession, Programme
        total_students = Student.objects.filter(status='active').count()
        pending_admissions = AdmissionApplication.objects.filter(status='pending').count()
        total_applications = AdmissionApplication.objects.count()
        current_session = AcademicSession.objects.filter(is_current=True).first()
        total_programmes = Programme.objects.count()
        recent_applications = AdmissionApplication.objects.order_by('-created_at')[:5]
        new_students = Student.objects.select_related('user', 'programme').order_by('-id')[:5]
        return {
            'dashboard_type': 'registrar',
            'total_students': total_students,
            'pending_admissions': pending_admissions,
            'total_applications': total_applications,
            'current_session': current_session,
            'total_programmes': total_programmes,
            'recent_applications': recent_applications,
            'new_students': new_students,
        }
    except Exception:
        return {'dashboard_type': 'registrar'}


def _get_librarian_dashboard_context():
    try:
        from library.models import Book, Borrowing, LibraryFine
        total_books = Book.objects.count()
        available_books = Book.objects.filter(available_copies__gt=0).count()
        active_borrowings = Borrowing.objects.filter(status='borrowed').count()
        overdue_borrowings = Borrowing.objects.filter(status='overdue').count()
        pending_fines = LibraryFine.objects.filter(status='pending').aggregate(
            total=Sum('amount'))['total'] or 0
        recent_borrowings = Borrowing.objects.filter(
            status='borrowed'
        ).select_related('book', 'borrower').order_by('-borrow_date')[:6]
        return {
            'dashboard_type': 'librarian',
            'total_books': total_books,
            'available_books': available_books,
            'active_borrowings': active_borrowings,
            'overdue_borrowings': overdue_borrowings,
            'pending_fines': pending_fines,
            'recent_borrowings': recent_borrowings,
        }
    except Exception:
        return {'dashboard_type': 'librarian'}


def _get_hostel_dashboard_context():
    try:
        from hostel.models import Hostel, Room, RoomAllocation, MaintenanceRequest
        total_hostels = Hostel.objects.filter(is_active=True).count()
        total_rooms = Room.objects.count()
        occupied_rooms = RoomAllocation.objects.filter(is_active=True).count()
        available_rooms = Room.objects.filter(is_available=True).count()
        pending_maintenance = MaintenanceRequest.objects.filter(status='pending').count()
        recent_allocations = RoomAllocation.objects.filter(
            is_active=True
        ).select_related('student__user', 'room__hostel').order_by('-allocation_date')[:6]
        hostels = Hostel.objects.filter(is_active=True)
        return {
            'dashboard_type': 'hostel_manager',
            'total_hostels': total_hostels,
            'total_rooms': total_rooms,
            'occupied_rooms': occupied_rooms,
            'available_rooms': available_rooms,
            'pending_maintenance': pending_maintenance,
            'recent_allocations': recent_allocations,
            'hostels': hostels,
        }
    except Exception:
        return {'dashboard_type': 'hostel_manager'}


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)

    context = {'form': form}
    user = request.user

    if user.is_student:
        context.update(_get_student_profile_context(user))
    elif user.is_lecturer:
        context.update(_get_lecturer_profile_context(user))
    elif user.is_finance_staff:
        context.update(_get_finance_profile_context(user))
    elif user.is_registrar:
        context.update(_get_registrar_profile_context(user))
    elif user.is_librarian:
        context.update(_get_librarian_profile_context(user))
    elif user.role == 'hostel_manager':
        context.update(_get_hostel_profile_context(user))
    elif user.is_admin or user.is_superuser:
        context.update(_get_admin_profile_context())

    return render(request, 'accounts/profile.html', context)


def _get_student_profile_context(user):
    try:
        from students.models import Student, Enrollment
        from academics.models import StudentResult
        from finance.models import Invoice
        student = Student.objects.select_related(
            'programme', 'current_year', 'current_semester_number'
        ).get(user=user)
        enrollments = Enrollment.objects.filter(
            student=student, is_active=True
        ).select_related('course', 'semester')
        results = StudentResult.objects.filter(
            student=student, is_published=True
        ).select_related('course_allocation__course').order_by('-id')[:10]
        invoices = Invoice.objects.filter(student=student).select_related('session').order_by('-issued_date')[:5]
        total_billed = sum(inv.total_amount for inv in Invoice.objects.filter(student=student))
        total_paid = sum(inv.amount_paid for inv in Invoice.objects.filter(student=student))
        balance = total_billed - total_paid
        cgpa = student.calculate_cgpa()
        return {
            'profile_role': 'student',
            'student': student,
            'enrollments': enrollments,
            'results': results,
            'invoices': invoices,
            'total_billed': total_billed,
            'total_paid': total_paid,
            'balance': balance,
            'cgpa': cgpa,
        }
    except Exception:
        return {'profile_role': 'student'}


def _get_lecturer_profile_context(user):
    try:
        from staff.models import StaffProfile, StaffPerformance
        from academics.models import CourseAllocation
        staff = StaffProfile.objects.select_related('department', 'user').get(user=user)
        allocations = CourseAllocation.objects.filter(
            lecturer=staff
        ).select_related('course', 'semester').order_by('-id')[:10]
        performances = StaffPerformance.objects.filter(staff=staff).select_related('semester', 'evaluated_by').order_by('-created_at')[:5]
        return {
            'profile_role': 'lecturer',
            'staff': staff,
            'allocations': allocations,
            'performances': performances,
        }
    except Exception:
        return {'profile_role': 'lecturer'}


def _get_finance_profile_context(user):
    try:
        from finance.models import Invoice, Payment
        recent_invoices = Invoice.objects.filter(
            created_by=user
        ).select_related('student__user', 'session').order_by('-issued_date')[:8]
        recent_payments = Payment.objects.filter(
            processed_by=user
        ).select_related('student__user').order_by('-payment_date')[:8]
        total_processed = Payment.objects.filter(
            processed_by=user, status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        return {
            'profile_role': 'finance',
            'recent_invoices': recent_invoices,
            'recent_payments': recent_payments,
            'total_processed': total_processed,
        }
    except Exception:
        return {'profile_role': 'finance'}


def _get_registrar_profile_context(user):
    try:
        from students.models import AdmissionApplication
        reviewed = AdmissionApplication.objects.filter(
            reviewed_by=user
        ).order_by('-application_date')[:8]
        total_reviewed = AdmissionApplication.objects.filter(reviewed_by=user).count()
        return {
            'profile_role': 'registrar',
            'reviewed_applications': reviewed,
            'total_reviewed': total_reviewed,
        }
    except Exception:
        return {'profile_role': 'registrar'}


def _get_librarian_profile_context(user):
    try:
        from library.models import Borrowing, LibraryFine
        issued = Borrowing.objects.filter(
            issued_by=user
        ).select_related('book', 'borrower').order_by('-borrow_date')[:8]
        total_issued = Borrowing.objects.filter(issued_by=user).count()
        pending_fines = LibraryFine.objects.filter(status='pending').aggregate(
            total=Sum('amount'))['total'] or 0
        return {
            'profile_role': 'librarian',
            'issued_books': issued,
            'total_issued': total_issued,
            'pending_fines': pending_fines,
        }
    except Exception:
        return {'profile_role': 'librarian'}


def _get_hostel_profile_context(user):
    try:
        from hostel.models import Hostel, RoomAllocation, MaintenanceRequest
        managed_hostels = Hostel.objects.filter(warden=user)
        allocations = RoomAllocation.objects.filter(
            allocated_by=user, is_active=True
        ).select_related('student__user', 'room__hostel').order_by('-allocation_date')[:8]
        total_allocations = RoomAllocation.objects.filter(allocated_by=user).count()
        pending_maintenance = MaintenanceRequest.objects.filter(status='pending').count()
        return {
            'profile_role': 'hostel_manager',
            'managed_hostels': managed_hostels,
            'allocations': allocations,
            'total_allocations': total_allocations,
            'pending_maintenance': pending_maintenance,
        }
    except Exception:
        return {'profile_role': 'hostel_manager'}


def _get_admin_profile_context():
    try:
        from students.models import Student
        from staff.models import StaffProfile
        from accounts.models import User
        total_users = User.objects.count()
        total_students = Student.objects.filter(status='active').count()
        total_staff = StaffProfile.objects.count()
        recent_users = User.objects.order_by('-date_joined')[:8]
        return {
            'profile_role': 'admin',
            'total_users': total_users,
            'total_students': total_students,
            'total_staff': total_staff,
            'recent_users': recent_users,
        }
    except Exception:
        return {'profile_role': 'admin'}


@login_required
@role_required(['admin', 'registrar'])
def user_list_view(request):
    users = User.objects.all()
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)
    return render(request, 'accounts/user_list.html', {
        'users': users,
        'roles': User.Role.choices,
    })


@login_required
@role_required(['admin'])
def register_user_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} created successfully.')
            return redirect('accounts:user_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register_user.html', {'form': form})


_QC_ACTION_ROLES = {
    'add_user':        ['admin'],
    'new_admission':   ['admin', 'registrar'],
    'create_invoice':  ['admin', 'finance'],
    'record_payment':  ['admin', 'finance'],
    'issue_book':      ['admin', 'librarian'],
    'add_book':        ['admin', 'librarian'],
    'allocate_room':   ['admin', 'hostel_manager'],
    'add_maintenance': ['admin', 'hostel_manager', 'student'],
    'register_course': ['student'],
}


@login_required
def quick_create_view(request, action):
    from django.http import JsonResponse, HttpResponse
    from django.template.loader import render_to_string

    user = request.user
    allowed = _QC_ACTION_ROLES.get(action)
    if allowed is None:
        return HttpResponse('Unknown action', status=404)
    if not user.is_superuser and user.role not in allowed:
        return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)

    if request.method == 'GET':
        ctx = _qc_get_context(action, user)
        html = render_to_string(f'accounts/quick_create/{action}.html', ctx, request=request)
        return HttpResponse(html)

    return JsonResponse(_qc_handle_post(action, request))


def _qc_get_context(action, user):
    ctx = {}
    try:
        if action == 'add_user':
            ctx['roles'] = User.Role.choices

        elif action == 'new_admission':
            from academics.models import Programme, AcademicSession, Intake
            from finance.models import FeeStructure
            ctx['programmes'] = Programme.objects.select_related('department').all()
            ctx['sessions'] = AcademicSession.objects.all().order_by('-name')
            ctx['intakes'] = Intake.objects.all().order_by('-created_at')
            ctx['fee_structures'] = FeeStructure.objects.filter(is_mandatory=True).select_related('programme').all()

        elif action == 'create_invoice':
            from academics.models import AcademicSession, StudySemester
            from students.models import Student
            ctx['students'] = Student.objects.select_related('user').filter(
                status__in=['active', 'admitted']).order_by('student_id')
            ctx['sessions'] = AcademicSession.objects.all().order_by('-name')
            ctx['semesters'] = StudySemester.objects.all()

        elif action == 'record_payment':
            from students.models import Student
            from finance.models import Invoice
            ctx['students'] = Student.objects.select_related('user').filter(
                status__in=['active', 'admitted']).order_by('student_id')
            ctx['invoices'] = Invoice.objects.select_related('student__user').exclude(
                status='paid').order_by('-issued_date')[:200]
            ctx['methods'] = [
                ('cash', 'Cash'), ('bank_transfer', 'Bank Transfer'),
                ('card', 'Card Payment'), ('mobile_money', 'Mobile Money'), ('cheque', 'Cheque'),
            ]

        elif action == 'issue_book':
            from library.models import Book
            from accounts.models import User
            ctx['books'] = Book.objects.filter(available_copies__gt=0).order_by('title')
            ctx['users'] = User.objects.filter(is_active=True).order_by('first_name')

        elif action == 'add_book':
            from library.models import BookCategory
            ctx['categories'] = BookCategory.objects.all()

        elif action == 'allocate_room':
            from students.models import Student
            from hostel.models import Room
            ctx['students'] = Student.objects.select_related('user').filter(
                status='active').order_by('student_id')
            ctx['rooms'] = Room.objects.select_related('hostel').filter(
                is_available=True).order_by('hostel__name', 'room_number')

        elif action == 'add_maintenance':
            from hostel.models import Room
            ctx['rooms'] = Room.objects.select_related('hostel').all().order_by('hostel__name', 'room_number')
            ctx['priorities'] = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')]

        elif action == 'register_course':
            from students.models import Student, Enrollment
            from academics.models import Course
            try:
                student = Student.objects.get(user=user)
                enrolled_ids = Enrollment.objects.filter(student=student, is_active=True).values_list('course_id', flat=True)
                if student.programme:
                    courses = Course.objects.filter(
                        programme=student.programme, is_active=True
                    ).exclude(id__in=enrolled_ids)
                else:
                    courses = Course.objects.filter(is_active=True).exclude(id__in=enrolled_ids)
                ctx['courses'] = courses
                ctx['student'] = student
            except Student.DoesNotExist:
                ctx['courses'] = []
    except Exception:
        pass
    return ctx


def _qc_handle_post(action, request):
    try:
        if action == 'add_user':
            return _qcp_add_user(request)
        elif action == 'new_admission':
            return _qcp_new_admission(request)
        elif action == 'create_invoice':
            return _qcp_create_invoice(request)
        elif action == 'record_payment':
            return _qcp_record_payment(request)
        elif action == 'issue_book':
            return _qcp_issue_book(request)
        elif action == 'add_book':
            return _qcp_add_book(request)
        elif action == 'allocate_room':
            return _qcp_allocate_room(request)
        elif action == 'add_maintenance':
            return _qcp_add_maintenance(request)
        elif action == 'register_course':
            return _qcp_register_course(request)
        return {'success': False, 'message': 'Unknown action'}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def _qcp_add_user(request):
    from django.contrib.auth.hashers import make_password
    username = request.POST.get('username', '').strip()
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    email = request.POST.get('email', '').strip()
    role = request.POST.get('role', 'student')
    password = request.POST.get('password', '').strip()
    if not username or not password:
        return {'success': False, 'message': 'Username and password are required.'}
    if User.objects.filter(username=username).exists():
        return {'success': False, 'message': f'Username "{username}" already taken.'}
    user = User.objects.create(
        username=username, first_name=first_name, last_name=last_name,
        email=email, role=role, password=make_password(password),
    )
    return {'success': True, 'message': f'User "{user.username}" created.', 'redirect': '/accounts/users/'}


def _qcp_new_admission(request):
    from students.models import AdmissionApplication
    from academics.models import Programme, AcademicSession
    from finance.models import FeeStructure, StudentFee
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    dob = request.POST.get('date_of_birth') or None
    gender = request.POST.get('gender', 'M')
    programme_id = request.POST.get('programme')
    session_id = request.POST.get('session')
    intake_id = request.POST.get('intake') or None
    selected_fee_ids = request.POST.getlist('fees')
    if not first_name or not last_name or not programme_id or not session_id:
        return {'success': False, 'message': 'Name, programme and session are required.'}
    programme = Programme.objects.get(pk=programme_id)
    session = AcademicSession.objects.get(pk=session_id)
    app = AdmissionApplication.objects.create(
        first_name=first_name, last_name=last_name, email=email, phone=phone,
        date_of_birth=dob or '2000-01-01', gender=gender,
        programme_applied=programme, session=session, intake_id=intake_id,
    )
    
    # Create student fee assignments if selected
    if selected_fee_ids:
        for fee_id in selected_fee_ids:
            try:
                fee = FeeStructure.objects.get(pk=fee_id)
                StudentFee.objects.create(
                    student=app,
                    fee_structure=fee,
                    session=session,
                    is_active=True,
                    notes=f'Assigned on admission'
                )
            except FeeStructure.DoesNotExist:
                pass
    
    return {'success': True, 'message': f'Admission application for {app.first_name} {app.last_name} submitted.',
            'redirect': '/students/admissions/'}


def _qcp_create_invoice(request):
    from students.models import Student
    from academics.models import AcademicSession
    from finance.models import Invoice, InvoiceItem
    student_id = request.POST.get('student')
    session_id = request.POST.get('session')
    semester_id = request.POST.get('semester') or None
    due_date = request.POST.get('due_date') or None
    description = request.POST.get('description', '').strip()
    amount = request.POST.get('amount', '0')
    if not student_id or not session_id or not description:
        return {'success': False, 'message': 'Student, session and at least one item required.'}
    student = Student.objects.get(pk=student_id)
    session = AcademicSession.objects.get(pk=session_id)
    invoice = Invoice.objects.create(
        student=student, session=session, semester_id=semester_id,
        total_amount=float(amount), due_date=due_date, created_by=request.user,
    )
    InvoiceItem.objects.create(invoice=invoice, description=description, amount=float(amount))
    return {'success': True, 'message': f'Invoice {invoice.invoice_number} created.',
            'redirect': f'/finance/invoices/{invoice.pk}/'}


def _qcp_record_payment(request):
    from finance.models import Invoice, Payment
    invoice_id = request.POST.get('invoice')
    amount = request.POST.get('amount', '0')
    method = request.POST.get('payment_method', 'cash')
    reference = request.POST.get('reference_number', '')
    notes = request.POST.get('notes', '')
    if not invoice_id or not amount:
        return {'success': False, 'message': 'Invoice and amount are required.'}
    invoice = Invoice.objects.select_related('student').get(pk=invoice_id)
    payment = Payment.objects.create(
        invoice=invoice, student=invoice.student, amount=float(amount),
        payment_method=method, reference_number=reference, notes=notes,
        status='completed', processed_by=request.user,
    )
    return {'success': True, 'message': f'Payment {payment.receipt_number} recorded.',
            'redirect': f'/finance/invoices/{invoice.pk}/'}


def _qcp_issue_book(request):
    from library.models import Book, Borrowing
    book_id = request.POST.get('book')
    user_id = request.POST.get('borrower')
    due_date = request.POST.get('due_date')
    if not book_id or not user_id or not due_date:
        return {'success': False, 'message': 'Book, borrower and due date are required.'}
    book = Book.objects.get(pk=book_id)
    borrower = User.objects.get(pk=user_id)
    if book.available_copies <= 0:
        return {'success': False, 'message': 'No copies available for this book.'}
    Borrowing.objects.create(book=book, borrower=borrower, due_date=due_date, issued_by=request.user)
    return {'success': True, 'message': f'"{book.title}" issued to {borrower.get_full_name()}.',
            'redirect': '/library/borrowings/'}


def _qcp_add_book(request):
    from library.models import Book, BookCategory
    title = request.POST.get('title', '').strip()
    author = request.POST.get('author', '').strip()
    isbn = request.POST.get('isbn', '').strip()
    cat_id = request.POST.get('category') or None
    copies = int(request.POST.get('total_copies', 1) or 1)
    publisher = request.POST.get('publisher', '')
    pub_year = request.POST.get('publication_year') or None
    if not title or not author or not isbn:
        return {'success': False, 'message': 'Title, author and ISBN are required.'}
    if Book.objects.filter(isbn=isbn).exists():
        return {'success': False, 'message': f'A book with ISBN "{isbn}" already exists.'}
    book = Book.objects.create(
        title=title, author=author, isbn=isbn, category_id=cat_id,
        total_copies=copies, available_copies=copies,
        publisher=publisher, publication_year=pub_year,
    )
    return {'success': True, 'message': f'Book "{book.title}" added to catalog.',
            'redirect': '/library/'}


def _qcp_allocate_room(request):
    from students.models import Student
    from hostel.models import Room, RoomAllocation
    from academics.models import AcademicSession
    student_id = request.POST.get('student')
    room_id = request.POST.get('room')
    if not student_id or not room_id:
        return {'success': False, 'message': 'Student and room are required.'}
    student = Student.objects.get(pk=student_id)
    room = Room.objects.get(pk=room_id)
    if room.is_full:
        return {'success': False, 'message': f'Room {room.room_number} is at full capacity.'}
    session = AcademicSession.objects.filter(is_current=True).first()
    RoomAllocation.objects.create(student=student, room=room, session=session, allocated_by=request.user)
    return {'success': True, 'message': f'Room {room.room_number} allocated to {student.user.get_full_name()}.',
            'redirect': '/hostel/'}


def _qcp_add_maintenance(request):
    from hostel.models import Room, MaintenanceRequest
    room_id = request.POST.get('room')
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()
    priority = request.POST.get('priority', 'medium')
    if not room_id or not title:
        return {'success': False, 'message': 'Room and title are required.'}
    room = Room.objects.get(pk=room_id)
    MaintenanceRequest.objects.create(
        room=room, issue=title, description=description,
        priority=priority, reported_by=request.user,
    )
    return {'success': True, 'message': f'Maintenance request "{title}" submitted.',
            'redirect': '/hostel/maintenance/'}


def _qcp_register_course(request):
    from students.models import Student, Enrollment
    from academics.models import Course, StudySemester
    course_ids = request.POST.getlist('courses')
    semester_id = request.POST.get('semester') or None
    if not course_ids:
        return {'success': False, 'message': 'Select at least one course.'}
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return {'success': False, 'message': 'Student profile not found.'}
    semester = StudySemester.objects.get(pk=semester_id) if semester_id else student.current_semester_number
    created = 0
    for cid in course_ids:
        course = Course.objects.get(pk=cid)
        _, new = Enrollment.objects.get_or_create(
            student=student, course=course,
            defaults={'semester': semester, 'is_active': True},
        )
        if new:
            created += 1
    return {'success': True, 'message': f'{created} course(s) registered successfully.',
            'redirect': '/students/my-courses/'}
