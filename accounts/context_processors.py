from django.db import models


def admin_dashboard_stats(request):
    """Add admin dashboard statistics to context."""
    context = {}
    if request.path.startswith('/admin/'):
        try:
            from students.models import Student
            from academics.models import Course
            from staff.models import StaffProfile
            from finance.models import Invoice

            context['total_students'] = Student.objects.filter(status='active').count()
            context['total_courses'] = Course.objects.filter(is_active=True).count()
            context['total_staff'] = StaffProfile.objects.filter(is_active=True).count()
            total_revenue = Invoice.objects.filter(status='paid').aggregate(
                total=models.Sum('total_amount'))['total'] or 0
            context['total_revenue'] = f"{total_revenue:,.0f}"
        except Exception:
            # Fallback if models don't exist or there's an error
            context['total_students'] = 0
            context['total_courses'] = 0
            context['total_staff'] = 0
            context['total_revenue'] = "0"
    return context


def user_context(request):
    """Add user role and navigation context to all templates."""
    context = {}
    if request.user.is_authenticated:
        user = request.user
        context['user_role'] = user.role
        context['user_role_display'] = user.get_role_display()
        context['is_admin_user'] = user.is_admin
        context['is_staff_user'] = user.role in ['admin', 'registrar', 'lecturer', 'finance', 'librarian', 'hostel_manager']

        # Navigation items based on role
        nav_items = _get_nav_items(user)
        context['nav_items'] = nav_items
    return context


def _get_nav_items(user):
    """Return navigation items based on user role."""
    items = [
        {'label': 'Dashboard', 'url': 'accounts:dashboard', 'icon': 'bi-speedometer2'},
    ]

    if user.is_admin or user.is_superuser:
        items.extend([
            {'label': 'Users', 'url': 'accounts:user_list', 'icon': 'bi-people'},
            {'label': 'Students', 'url': 'students:student_list', 'icon': 'bi-mortarboard'},
            {'label': 'Faculties', 'url': 'academics:faculty_list', 'icon': 'bi-building'},
            {'label': 'Programmes', 'url': 'academics:programme_list', 'icon': 'bi-journal-bookmark'},
            {'label': 'Courses', 'url': 'academics:course_list', 'icon': 'bi-book'},
            {'label': 'Study Levels', 'url': 'academics:study_level_list', 'icon': 'bi-layers'},
            {'label': 'Staff', 'url': 'staff:staff_list', 'icon': 'bi-person-badge'},
            {'label': 'Finance', 'url': 'finance:dashboard', 'icon': 'bi-cash-stack'},
            {'label': 'Library', 'url': 'library:catalog', 'icon': 'bi-journal-bookmark'},
            {'label': 'Hostel', 'url': 'hostel:dashboard', 'icon': 'bi-building'},
            {'label': 'Communications', 'url': 'communications:announcements', 'icon': 'bi-megaphone'},
            {'label': 'Reports', 'url': 'reports:dashboard', 'icon': 'bi-graph-up'},
        ])
    elif user.is_registrar:
        items.extend([
            {'label': 'Students', 'url': 'students:student_list', 'icon': 'bi-mortarboard'},
            {'label': 'Admissions', 'url': 'students:admission_list', 'icon': 'bi-person-plus'},
            {'label': 'Campuses', 'url': 'academics:campus_list', 'icon': 'bi-geo-alt'},
            {'label': 'Faculties', 'url': 'academics:faculty_list', 'icon': 'bi-building'},
            {'label': 'Programmes', 'url': 'academics:programme_list', 'icon': 'bi-journal-bookmark'},
            {'label': 'Courses', 'url': 'academics:course_list', 'icon': 'bi-book'},
            {'label': 'Study Levels', 'url': 'academics:study_level_list', 'icon': 'bi-layers'},
            {'label': 'Sessions', 'url': 'academics:session_list', 'icon': 'bi-calendar3'},
            {'label': 'Intakes', 'url': 'academics:intake_list', 'icon': 'bi-people-plus'},
            {'label': 'Staff', 'url': 'staff:staff_list', 'icon': 'bi-person-badge'},
            {'label': 'Communications', 'url': 'communications:announcements', 'icon': 'bi-megaphone'},
            {'label': 'Reports', 'url': 'reports:dashboard', 'icon': 'bi-graph-up'},
        ])
    elif user.is_lecturer:
        items.extend([
            {'label': 'My Courses', 'url': 'staff:my_courses', 'icon': 'bi-book'},
            {'label': 'Grades', 'url': 'academics:grade_management', 'icon': 'bi-card-checklist'},
            {'label': 'Attendance', 'url': 'academics:attendance_list', 'icon': 'bi-clipboard-check'},
            {'label': 'Communications', 'url': 'communications:announcements', 'icon': 'bi-megaphone'},
        ])
    elif user.is_department_head:
        # Department head: include departmental quick links, and link to own department if assigned
        try:
            from academics.models import Department
            from django.urls import reverse
            dept = Department.objects.filter(head_of_department=user).first()
            dept_path = reverse('academics:department_detail', args=[dept.pk]) if dept else None
        except Exception:
            dept_path = None

        items.extend([
            {'label': 'Department', 'url': 'academics:department_list', 'icon': 'bi-building'},
            {'label': 'Programmes', 'url': 'academics:programme_list', 'icon': 'bi-journal-bookmark'},
            {'label': 'Courses', 'url': 'academics:course_list', 'icon': 'bi-book'},
            {'label': 'Students', 'url': 'students:student_list', 'icon': 'bi-people'},
            {'label': 'Grades', 'url': 'academics:grade_management', 'icon': 'bi-card-checklist'},
            {'label': 'Attendance', 'url': 'academics:attendance_list', 'icon': 'bi-clipboard-check'},
            {'label': 'Timetable', 'url': 'academics:my_timetable', 'icon': 'bi-calendar-week'},
            {'label': 'Staff', 'url': 'staff:staff_list', 'icon': 'bi-person-badge'},
            {'label': 'Reports', 'url': 'reports:dashboard', 'icon': 'bi-graph-up'},
        ])

        if dept_path:
            # put a direct quick link to the specific department detail page
            items.insert(1, {'label': 'My Department', 'path': dept_path, 'icon': 'bi-building'})
    elif user.is_programme_coordinator:
        try:
            from academics.models import Programme
            from django.urls import reverse
            programme = Programme.objects.filter(coordinator=user).first()
            programme_path = reverse('academics:programme_detail', args=[programme.pk]) if programme else None
        except Exception:
            programme_path = None

        items.extend([
            {'label': 'Programmes', 'url': 'academics:programme_list', 'icon': 'bi-journal-bookmark'},
            {'label': 'Courses', 'url': 'academics:course_list', 'icon': 'bi-book'},
            {'label': 'Students', 'url': 'students:student_list', 'icon': 'bi-people'},
            {'label': 'Grades', 'url': 'academics:grade_management', 'icon': 'bi-card-checklist'},
            {'label': 'Attendance', 'url': 'academics:attendance_list', 'icon': 'bi-clipboard-check'},
            {'label': 'Timetable', 'url': 'academics:my_timetable', 'icon': 'bi-calendar-week'},
            {'label': 'Staff', 'url': 'staff:staff_list', 'icon': 'bi-person-badge'},
            {'label': 'Reports', 'url': 'reports:dashboard', 'icon': 'bi-graph-up'},
        ])

        if programme_path:
            items.insert(1, {'label': 'My Programme', 'path': programme_path, 'icon': 'bi-journal-bookmark'})
    elif getattr(user, 'is_faculty_dean', False):
        try:
            from academics.models import Faculty
            from django.urls import reverse
            faculty = Faculty.objects.filter(dean=user).first()
            faculty_path = reverse('academics:faculty_detail', args=[faculty.pk]) if faculty else None
        except Exception:
            faculty_path = None

        items.extend([
            {'label': 'Faculty', 'url': 'academics:faculty_list', 'icon': 'bi-building'},
            {'label': 'Departments', 'url': 'academics:department_list', 'icon': 'bi-building'},
            {'label': 'Programmes', 'url': 'academics:programme_list', 'icon': 'bi-journal-bookmark'},
            {'label': 'Courses', 'url': 'academics:course_list', 'icon': 'bi-book'},
            {'label': 'Students', 'url': 'students:student_list', 'icon': 'bi-people'},
            {'label': 'Staff', 'url': 'staff:staff_list', 'icon': 'bi-person-badge'},
            {'label': 'Reports', 'url': 'reports:dashboard', 'icon': 'bi-graph-up'},
        ])

        if faculty_path:
            items.insert(1, {'label': 'My Faculty', 'path': faculty_path, 'icon': 'bi-building'})
    elif user.is_student:
        items.extend([
            {'label': 'My Courses', 'url': 'students:my_courses', 'icon': 'bi-book'},
            {'label': 'Register Courses', 'url': 'students:course_registration', 'icon': 'bi-plus-circle'},
            {'label': 'Results', 'url': 'students:my_results', 'icon': 'bi-trophy'},
            {'label': 'Finance', 'url': 'finance:my_fees', 'icon': 'bi-cash-stack'},
            {'label': 'Library', 'url': 'library:my_books', 'icon': 'bi-journal-bookmark'},
            {'label': 'Timetable', 'url': 'academics:my_timetable', 'icon': 'bi-calendar-week'},
        ])
    elif user.is_finance_staff:
        items.extend([
            {'label': 'Finance', 'url': 'finance:dashboard', 'icon': 'bi-cash-stack'},
            {'label': 'Students', 'url': 'finance:students', 'icon': 'bi-mortarboard'},
            {'label': 'Invoices', 'url': 'finance:invoice_list', 'icon': 'bi-receipt'},
            {'label': 'Payments', 'url': 'finance:payment_list', 'icon': 'bi-credit-card'},
            {'label': 'Fee Structure', 'url': 'finance:fee_structure', 'icon': 'bi-gear'},
            {'label': 'Reports', 'url': 'reports:financial', 'icon': 'bi-graph-up'},
        ])
    elif user.is_librarian:
        items.extend([
            {'label': 'Catalog', 'url': 'library:catalog', 'icon': 'bi-journal-bookmark'},
            {'label': 'Book Management', 'url': 'library:book_list', 'icon': 'bi-list-ul'},
            {'label': 'Issue Book', 'url': 'library:issue_book', 'icon': 'bi-box-arrow-right'},
            {'label': 'Borrowings', 'url': 'library:borrowing_list', 'icon': 'bi-arrow-left-right'},
            {'label': 'Fines', 'url': 'library:fine_list', 'icon': 'bi-exclamation-triangle'},
        ])
    elif user.role == 'hostel_manager':
        items.extend([
            {'label': 'Hostel', 'url': 'hostel:dashboard', 'icon': 'bi-building'},
            {'label': 'Rooms', 'url': 'hostel:room_list', 'icon': 'bi-house-door'},
            {'label': 'Allocations', 'url': 'hostel:allocate_room', 'icon': 'bi-person-check'},
            {'label': 'Maintenance', 'url': 'hostel:maintenance_list', 'icon': 'bi-tools'},
            {'label': 'Communications', 'url': 'communications:announcements', 'icon': 'bi-megaphone'},
        ])

    # Filter out any nav items that don't provide either a concrete `path`
    # or a non-empty named `url` to avoid template reverse errors.
    filtered = [
        i for i in items
        if i.get('path') or (i.get('url') and str(i.get('url')).strip())
    ]
    return filtered
