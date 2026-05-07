from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, Q
from django.http import HttpResponse
from accounts.decorators import role_required


@login_required
@role_required(['admin', 'registrar', 'finance'])
def reports_dashboard(request):
    from students.models import Student
    from academics.models import Course, Department
    from finance.models import Payment, Invoice
    from staff.models import StaffProfile

    context = {
        'total_students': Student.objects.count(),
        'active_students': Student.objects.filter(status='active').count(),
        'total_courses': Course.objects.filter(is_active=True).count(),
        'total_departments': Department.objects.filter(is_active=True).count(),
        'total_staff': StaffProfile.objects.filter(is_active=True).count(),
        'total_revenue': Payment.objects.filter(status='completed').aggregate(
            total=Sum('amount'))['total'] or 0,
        'pending_payments': Invoice.objects.filter(
            status__in=['pending', 'partial']).aggregate(
            total=Sum('balance'))['total'] or 0,
    }

    # Student distribution by year and semester
    level_distribution = Student.objects.filter(status='active').values(
        'current_year', 'current_semester_number').annotate(count=Count('id')).order_by('current_year', 'current_semester_number')
    context['level_distribution'] = list(level_distribution)

    # Department-wise student count
    dept_students = Student.objects.filter(status='active').values(
        'programme__department__name').annotate(count=Count('id'))
    context['dept_students'] = list(dept_students)

    return render(request, 'reports/dashboard.html', context)


@login_required
@role_required(['admin', 'finance'])
def financial_report(request):
    from finance.models import Payment, Invoice, FeeStructure
    from academics.models import AcademicSession

    session_id = request.GET.get('session')
    sessions = AcademicSession.objects.all()

    payments = Payment.objects.filter(status='completed')
    invoices = Invoice.objects.all()

    if session_id:
        invoices = invoices.filter(session_id=session_id)
        payments = payments.filter(invoice__session_id=session_id)

    total_billed = invoices.aggregate(total=Sum('total_amount'))['total'] or 0
    total_collected = payments.aggregate(total=Sum('amount'))['total'] or 0
    total_outstanding = invoices.filter(
        status__in=['pending', 'partial', 'overdue']
    ).aggregate(total=Sum('balance'))['total'] or 0

    # Monthly collection trend
    from django.db.models.functions import TruncMonth
    monthly_collection = payments.annotate(
        month=TruncMonth('payment_date')
    ).values('month').annotate(total=Sum('amount')).order_by('month')

    return render(request, 'reports/financial.html', {
        'sessions': sessions,
        'total_billed': total_billed,
        'total_collected': total_collected,
        'total_outstanding': total_outstanding,
        'collection_rate': round((total_collected / total_billed * 100), 1) if total_billed > 0 else 0,
        'monthly_collection': list(monthly_collection),
    })


@login_required
@role_required(['admin', 'registrar'])
def academic_report(request):
    from academics.models import StudentResult, Semester, Course
    from students.models import Student

    semester_id = request.GET.get('semester')
    from academics.models import Semester as SemesterModel
    semesters = SemesterModel.objects.all()

    results = StudentResult.objects.filter(is_published=True)
    if semester_id:
        results = results.filter(course_allocation__semester_id=semester_id)

    avg_gpa = results.aggregate(avg=Avg('grade_point'))['avg'] or 0
    pass_count = results.filter(grade_point__gte=1.0).count()
    fail_count = results.filter(grade_point__lt=1.0).count()
    total_results = results.count()

    grade_distribution = results.values('grade').annotate(count=Count('id')).order_by('grade')

    return render(request, 'reports/academic.html', {
        'semesters': semesters,
        'avg_gpa': round(avg_gpa, 2),
        'pass_count': pass_count,
        'fail_count': fail_count,
        'total_results': total_results,
        'pass_rate': round((pass_count / total_results * 100), 1) if total_results > 0 else 0,
        'grade_distribution': list(grade_distribution),
    })


@login_required
@role_required(['admin', 'registrar'])
def attendance_report(request):
    from academics.models import Attendance, CourseAllocation

    allocations = CourseAllocation.objects.filter(
        semester__is_current=True
    ).select_related('course', 'lecturer')

    attendance_stats = []
    for alloc in allocations:
        total = Attendance.objects.filter(course_allocation=alloc).count()
        present = Attendance.objects.filter(course_allocation=alloc, is_present=True).count()
        rate = round((present / total * 100), 1) if total > 0 else 0
        attendance_stats.append({
            'course': alloc.course.code,
            'title': alloc.course.title,
            'lecturer': str(alloc.lecturer),
            'total_classes': total,
            'avg_attendance': rate,
        })

    return render(request, 'reports/attendance.html', {
        'attendance_stats': attendance_stats,
    })


@login_required
@role_required(['admin'])
def export_students_excel(request):
    """Export student data to Excel."""
    import openpyxl
    from students.models import Student

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Students'
    headers = ['Student ID', 'Name', 'Programme', 'Level', 'Status', 'Email', 'Phone']
    ws.append(headers)

    for student in Student.objects.select_related('user', 'programme').all():
        ws.append([
            student.student_id,
            student.full_name,
            str(student.programme) if student.programme else '',
            student.level_display,
            student.get_status_display(),
            student.user.email,
            student.user.phone_number,
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=students_report.xlsx'
    wb.save(response)
    return response
