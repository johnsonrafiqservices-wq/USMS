from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import date
from accounts.decorators import role_required, finance_required
from .models import FeeStructure, Invoice, InvoiceItem, Payment, Scholarship


@login_required
@finance_required
def student_payment_history(request, student_id):
    from students.models import Student
    from academics.models import AcademicSession, StudySemester
    student = get_object_or_404(Student, pk=student_id)
    
    invoices = Invoice.objects.filter(student=student).select_related('session', 'semester').order_by('-issued_date')
    payments = Payment.objects.filter(invoice__student=student).select_related('invoice', 'processed_by').order_by('-payment_date')
    
    # Filters
    session_filter = request.GET.get('session')
    semester_filter = request.GET.get('semester')
    
    if session_filter:
        invoices = invoices.filter(session_id=session_filter)
        payments = payments.filter(invoice__session_id=session_filter)
    if semester_filter:
        invoices = invoices.filter(semester_id=semester_filter)
        payments = payments.filter(invoice__semester_id=semester_filter)
    
    sessions = AcademicSession.objects.all()
    semesters = StudySemester.objects.all()
    
    # Calculate totals
    total_billed = sum(inv.total_amount for inv in invoices)
    total_paid = sum(pay.amount for pay in payments)
    total_balance = sum(inv.balance for inv in invoices)
    
    return render(request, 'finance/student_payment_history.html', {
        'student': student,
        'invoices': invoices,
        'payments': payments,
        'sessions': sessions,
        'semesters': semesters,
        'session_filter': session_filter,
        'semester_filter': semester_filter,
        'total_billed': total_billed,
        'total_paid': total_paid,
        'total_balance': total_balance,
    })


@login_required
@finance_required
def finance_students(request):
    from students.models import Student
    from academics.models import StudyYear, StudySemester
    from academics.models import Programme, Intake
    from django.db.models import Sum, Count
    students = Student.objects.select_related('user', 'programme', 'current_year', 'current_semester_number', 'intake').filter(
        status__in=['active', 'admitted']
    ).annotate(
        total_billed=Sum('invoices__total_amount'),
        total_paid=Sum('invoices__amount_paid'),
        total_balance=Sum('invoices__balance'),
        invoice_count=Count('invoices'),
        payment_count=Count('payments')
    ).order_by('student_id')
    
    search = request.GET.get('search')
    programme_filter = request.GET.get('programme')
    intake_filter = request.GET.get('intake')
    year_filter = request.GET.get('year')
    semester_filter = request.GET.get('semester')
    
    if search:
        students = students.filter(
            Q(student_id__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search)
        )
    if programme_filter:
        students = students.filter(programme_id=programme_filter)
    if intake_filter:
        students = students.filter(intake_id=intake_filter)
    if year_filter:
        students = students.filter(current_year_id=year_filter)
    if semester_filter:
        students = students.filter(current_semester_number_id=semester_filter)
    
    programmes = Programme.objects.all()
    intakes = Intake.objects.all()
    years = StudyYear.objects.all()
    semesters = StudySemester.objects.all()
    
    return render(request, 'finance/finance_students.html', {
        'students': students,
        'programmes': programmes,
        'intakes': intakes,
        'years': years,
        'semesters': semesters,
        'programme_filter': programme_filter,
        'intake_filter': intake_filter,
        'year_filter': year_filter,
        'semester_filter': semester_filter,
    })


@login_required
@finance_required
def finance_dashboard(request):
    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount'))['total'] or 0
    pending_invoices = Invoice.objects.filter(status='pending').count()
    overdue_invoices = Invoice.objects.filter(status='overdue').count()
    partial_invoices = Invoice.objects.filter(status='partial').count()
    total_outstanding = Invoice.objects.filter(
        status__in=['pending', 'partial', 'overdue']
    ).aggregate(total=Sum('balance'))['total'] or 0
    total_invoiced = Invoice.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    collection_rate = round((float(total_revenue) / float(total_invoiced) * 100), 1) if total_invoiced else 0

    recent_payments = Payment.objects.filter(
        status='completed'
    ).select_related('student__user', 'invoice').order_by('-payment_date')[:10]

    overdue_list = Invoice.objects.filter(
        status='overdue'
    ).select_related('student__user', 'session').order_by('-balance')[:8]

    # Monthly revenue for current year (last 6 months)
    import json
    from dateutil.relativedelta import relativedelta
    months_data = []
    today = date.today()
    for i in range(5, -1, -1):
        m = today - relativedelta(months=i)
        rev = Payment.objects.filter(
            status='completed',
            payment_date__year=m.year,
            payment_date__month=m.month,
        ).aggregate(total=Sum('amount'))['total'] or 0
        months_data.append({'label': m.strftime('%b %Y'), 'value': float(rev)})

    scholarships_count = Scholarship.objects.filter(is_active=True).count()
    scholarships_total = Scholarship.objects.filter(is_active=True).aggregate(
        total=Sum('amount'))['total'] or 0

    return render(request, 'finance/dashboard.html', {
        'total_revenue': total_revenue,
        'pending_invoices': pending_invoices,
        'overdue_invoices': overdue_invoices,
        'partial_invoices': partial_invoices,
        'total_outstanding': total_outstanding,
        'total_invoiced': total_invoiced,
        'collection_rate': collection_rate,
        'recent_payments': recent_payments,
        'overdue_list': overdue_list,
        'monthly_data': json.dumps(months_data),
        'scholarships_count': scholarships_count,
        'scholarships_total': scholarships_total,
    })


@login_required
@finance_required
def invoice_list(request):
    invoices = Invoice.objects.select_related('student__user', 'session', 'semester').all()
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    session_filter = request.GET.get('session', '')

    if status_filter:
        invoices = invoices.filter(status=status_filter)
    if search:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search) |
            Q(student__student_id__icontains=search) |
            Q(student__user__first_name__icontains=search) |
            Q(student__user__last_name__icontains=search)
        )
    if session_filter:
        invoices = invoices.filter(session_id=session_filter)

    from academics.models import AcademicSession
    sessions = AcademicSession.objects.all().order_by('-id')

    total_amount = invoices.aggregate(t=Sum('total_amount'))['t'] or 0
    total_balance = invoices.aggregate(t=Sum('balance'))['t'] or 0

    return render(request, 'finance/invoice_list.html', {
        'invoices': invoices,
        'statuses': Invoice.Status.choices,
        'sessions': sessions,
        'status_filter': status_filter,
        'search': search,
        'session_filter': session_filter,
        'total_amount': total_amount,
        'total_balance': total_balance,
    })


@login_required
@finance_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.select_related('student__user', 'session', 'semester', 'created_by'),
        pk=pk
    )
    items = invoice.items.select_related('fee_structure')
    payments = invoice.payments.select_related('processed_by').order_by('-payment_date')
    return render(request, 'finance/invoice_detail.html', {
        'invoice': invoice,
        'items': items,
        'payments': payments,
    })


@login_required
@finance_required
def create_invoice(request):
    from academics.models import AcademicSession, StudySemester
    from students.models import Student
    from django.http import JsonResponse
    sessions = AcademicSession.objects.all().order_by('-id')
    semesters = StudySemester.objects.all()
    students = Student.objects.select_related('user', 'programme').filter(
        status__in=['active', 'admitted']
    ).order_by('student_id')

    if request.method == 'POST':
        student_id = request.POST.get('student')
        session_id = request.POST.get('session')
        semester_id = request.POST.get('semester') or None
        due_date = request.POST.get('due_date') or None
        notes = request.POST.get('notes', '')
        descriptions = request.POST.getlist('description')
        amounts = request.POST.getlist('amount')

        if not student_id or not session_id or not descriptions:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Please fill all required fields and add at least one item.'})
            messages.error(request, 'Please fill all required fields and add at least one item.')
        else:
            student = get_object_or_404(Student, pk=student_id)
            session = get_object_or_404(AcademicSession, pk=session_id)
            total = sum(float(a) for a in amounts if a)
            invoice = Invoice.objects.create(
                student=student,
                session=session,
                semester_id=semester_id,
                total_amount=total,
                due_date=due_date,
                notes=notes,
                created_by=request.user,
            )
            for desc, amt in zip(descriptions, amounts):
                if desc and amt:
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        description=desc,
                        amount=float(amt),
                    )
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Invoice {invoice.invoice_number} created successfully.',
                    'redirect': f'/finance/invoices/{invoice.pk}/'
                })
            messages.success(request, f'Invoice {invoice.invoice_number} created successfully.')
            return redirect('finance:invoice_detail', pk=invoice.pk)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'finance/create_invoice_fragment.html', {
            'sessions': sessions,
            'semesters': semesters,
            'students': students,
        })

    return render(request, 'finance/create_invoice.html', {
        'sessions': sessions,
        'semesters': semesters,
        'students': students,
    })


@login_required
@finance_required
def payment_list(request):
    payments = Payment.objects.select_related('student__user', 'invoice').all()
    search = request.GET.get('search', '')
    method_filter = request.GET.get('method', '')
    status_filter = request.GET.get('status', '')

    if search:
        payments = payments.filter(
            Q(receipt_number__icontains=search) |
            Q(student__student_id__icontains=search) |
            Q(student__user__first_name__icontains=search) |
            Q(student__user__last_name__icontains=search) |
            Q(reference_number__icontains=search)
        )
    if method_filter:
        payments = payments.filter(payment_method=method_filter)
    if status_filter:
        payments = payments.filter(status=status_filter)

    total_collected = payments.filter(status='completed').aggregate(t=Sum('amount'))['t'] or 0

    return render(request, 'finance/payment_list.html', {
        'payments': payments,
        'methods': Payment.PaymentMethod.choices,
        'statuses': Payment.Status.choices,
        'search': search,
        'method_filter': method_filter,
        'status_filter': status_filter,
        'total_collected': total_collected,
    })


@login_required
@finance_required
def record_payment(request, invoice_id):
    from django.http import JsonResponse
    invoice = get_object_or_404(
        Invoice.objects.select_related('student__user', 'session'),
        pk=invoice_id
    )
    if request.method == 'POST':
        amount = request.POST.get('amount')
        method = request.POST.get('payment_method')
        reference = request.POST.get('reference_number', '')
        notes = request.POST.get('notes', '')
        try:
            amt = float(amount)
            if amt <= 0:
                raise ValueError
        except (ValueError, TypeError):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Enter a valid positive amount.'})
            messages.error(request, 'Enter a valid positive amount.')
            return render(request, 'finance/record_payment.html', {'invoice': invoice})

        payment = Payment.objects.create(
            invoice=invoice,
            student=invoice.student,
            amount=amt,
            payment_method=method,
            reference_number=reference,
            notes=notes,
            status='completed',
            processed_by=request.user,
        )
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Payment of UGX {amt:,.0f} recorded. Receipt: {payment.receipt_number}',
                'redirect': f'/finance/invoices/{invoice.pk}/'
            })
        messages.success(
            request,
            f'Payment of UGX {amt:,.0f} recorded. Receipt: {payment.receipt_number}'
        )
        return redirect('finance:invoice_detail', pk=invoice.pk)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'finance/record_payment_fragment.html', {
            'invoice': invoice,
            'methods': Payment.PaymentMethod.choices,
        })

    return render(request, 'finance/record_payment.html', {
        'invoice': invoice,
        'methods': Payment.PaymentMethod.choices,
    })


@login_required
def my_fees(request):
    """Student-facing financial overview."""
    from students.models import Student
    try:
        student = Student.objects.select_related('programme').get(user=request.user)
        invoices = Invoice.objects.filter(
            student=student
        ).select_related('session', 'semester').order_by('-issued_date')
        payments = Payment.objects.filter(
            student=student, status='completed'
        ).select_related('invoice').order_by('-payment_date')
        total_paid = payments.aggregate(total=Sum('amount'))['total'] or 0
        total_invoiced = invoices.aggregate(total=Sum('total_amount'))['total'] or 0
        total_owed = invoices.aggregate(total=Sum('balance'))['total'] or 0
        scholarships = Scholarship.objects.filter(student=student, is_active=True)
        scholarship_total = scholarships.aggregate(total=Sum('amount'))['total'] or 0
    except Student.DoesNotExist:
        student = None
        invoices = Invoice.objects.none()
        payments = Payment.objects.none()
        scholarships = Scholarship.objects.none()
        total_paid = total_invoiced = total_owed = scholarship_total = 0

    return render(request, 'finance/my_fees.html', {
        'student': student,
        'invoices': invoices,
        'payments': payments,
        'scholarships': scholarships,
        'total_paid': total_paid,
        'total_invoiced': total_invoiced,
        'total_owed': total_owed,
        'scholarship_total': scholarship_total,
    })


@login_required
@finance_required
def fee_structure_list(request):
    from academics.models import AcademicSession
    fees = FeeStructure.objects.select_related('programme', 'session').all()
    session_filter = request.GET.get('session', '')
    type_filter = request.GET.get('type', '')
    programme_filter = request.GET.get('programme', '')
    sessions = AcademicSession.objects.all().order_by('-id')

    if session_filter:
        fees = fees.filter(session_id=session_filter)
    if type_filter:
        fees = fees.filter(fee_type=type_filter)
    if programme_filter:
        fees = fees.filter(programme_id=programme_filter)

    from academics.models import Programme
    programmes = Programme.objects.all()

    return render(request, 'finance/fee_structure.html', {
        'fees': fees,
        'sessions': sessions,
        'programmes': programmes,
        'fee_types': FeeStructure.FeeType.choices,
        'session_filter': session_filter,
        'type_filter': type_filter,
        'programme_filter': programme_filter,
    })


@login_required
@finance_required
def fee_structure_create(request):
    from academics.models import AcademicSession, Programme
    from django.http import JsonResponse
    sessions = AcademicSession.objects.all().order_by('-id')
    programmes = Programme.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        fee_type = request.POST.get('fee_type')
        frequency = request.POST.get('frequency', 'per_semester')
        programme_id = request.POST.get('programme')
        level = request.POST.get('level') or None
        session_id = request.POST.get('session')
        amount = request.POST.get('amount')
        is_mandatory = request.POST.get('is_mandatory') == 'on'
        description = request.POST.get('description', '')

        if not all([name, fee_type, session_id, amount]):
            return JsonResponse({'success': False, 'message': 'Please fill all required fields.'})
        else:
            fee = FeeStructure.objects.create(
                name=name,
                fee_type=fee_type,
                frequency=frequency,
                programme_id=programme_id if programme_id else None,
                level=int(level) if level else None,
                session_id=session_id,
                amount=amount,
                is_mandatory=is_mandatory,
                description=description,
            )
            return JsonResponse({
                'success': True,
                'message': f'Fee structure "{fee.name}" created successfully.'
            })

    return render(request, 'finance/fee_structure_form_fragment.html', {
        'sessions': sessions,
        'programmes': programmes,
        'fee_types': FeeStructure.FeeType.choices,
    })


@login_required
@finance_required
def fee_structure_edit(request, pk):
    from academics.models import AcademicSession, Programme
    from django.http import JsonResponse
    fee = get_object_or_404(FeeStructure, pk=pk)
    sessions = AcademicSession.objects.all().order_by('-id')
    programmes = Programme.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        fee_type = request.POST.get('fee_type')
        frequency = request.POST.get('frequency', 'per_semester')
        programme_id = request.POST.get('programme')
        level = request.POST.get('level') or None
        session_id = request.POST.get('session')
        amount = request.POST.get('amount')
        is_mandatory = request.POST.get('is_mandatory') == 'on'
        description = request.POST.get('description', '')

        if not all([name, fee_type, session_id, amount]):
            return JsonResponse({'success': False, 'message': 'Please fill all required fields.'})
        else:
            fee.name = name
            fee.fee_type = fee_type
            fee.frequency = frequency
            fee.programme_id = programme_id if programme_id else None
            fee.level = int(level) if level else None
            fee.session_id = session_id
            fee.amount = amount
            fee.is_mandatory = is_mandatory
            fee.description = description
            fee.save()
            return JsonResponse({
                'success': True,
                'message': f'Fee structure "{fee.name}" updated successfully.'
            })

    return render(request, 'finance/fee_structure_form_fragment.html', {
        'fee': fee,
        'sessions': sessions,
        'programmes': programmes,
        'fee_types': FeeStructure.FeeType.choices,
    })


@login_required
@finance_required
def fee_structure_delete(request, pk):
    fee = get_object_or_404(FeeStructure, pk=pk)
    if request.method == 'POST':
        fee.delete()
        messages.success(request, f'Fee structure "{fee.name}" deleted successfully.')
        return redirect('finance:fee_structure')
    return render(request, 'finance/fee_structure_delete.html', {'fee': fee})


@login_required
@finance_required
def generate_invoices(request):
    from academics.models import AcademicSession, StudySemester
    from students.models import Student
    from django.http import JsonResponse

    session_id = request.GET.get('session')
    semester_id = request.GET.get('semester')

    sessions = AcademicSession.objects.all().order_by('-name')
    semesters = StudySemester.objects.all()

    if request.method == 'POST':
        session_id = request.POST.get('session')
        semester_id = request.POST.get('semester') or None

        if not session_id:
            return JsonResponse({'success': False, 'message': 'Session is required.'})

        try:
            session = AcademicSession.objects.get(pk=session_id)
            semester = StudySemester.objects.get(pk=semester_id) if semester_id else None

            # Get active students with assigned fees
            students = Student.objects.filter(status='active').select_related('user', 'programme', 'current_year', 'current_semester_number')
            invoices_created = 0
            total_amount = 0
            errors = []

            for student in students:
                assigned_fees = StudentFee.objects.filter(
                    student=student,
                    session=session,
                    is_active=True
                ).select_related('fee_structure')

                if not assigned_fees.exists():
                    continue

                fees_to_bill = _get_fees_to_bill(assigned_fees, student, semester)

                if not fees_to_bill:
                    continue

                total = sum(fee.amount for fee in fees_to_bill)

                # Check if invoice already exists
                existing_invoice = Invoice.objects.filter(
                    student=student,
                    session=session,
                    semester=semester
                ).first()

                if existing_invoice:
                    continue

                # Create invoice
                invoice = Invoice.objects.create(
                    student=student,
                    session=session,
                    semester=semester,
                    total_amount=total,
                    created_by=request.user,
                )

                for fee in fees_to_bill:
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        description=f'{fee.name} ({fee.get_frequency_display()})',
                        amount=fee.amount,
                        fee_structure=fee
                    )

                invoices_created += 1
                total_amount += total

            return JsonResponse({
                'success': True,
                'message': f'Generated {invoices_created} invoices totaling UGX {total_amount:,.0f}',
                'invoices_created': invoices_created,
                'total_amount': total_amount
            })

        except AcademicSession.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid session.'})
        except StudySemester.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid semester.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return render(request, 'finance/generate_invoices.html', {
        'sessions': sessions,
        'semesters': semesters,
        'session_filter': session_id,
        'semester_filter': semester_id,
    })


def _get_fees_to_bill(assigned_fees, student, semester):
    """Determine which fees should be billed based on frequency."""
    fees_to_bill = []
    current_year = student.current_year
    current_semester = student.current_semester_number

    for assignment in assigned_fees:
        fee = assignment.fee_structure

        if fee.programme and fee.programme != student.programme:
            continue

        if fee.level and fee.level != current_year:
            continue

        if fee.frequency == FeeStructure.Frequency.PER_SEMESTER:
            fees_to_bill.append(fee)

        elif fee.frequency == FeeStructure.Frequency.PER_YEAR:
            if current_semester and current_semester.name.lower() in ['semester 1', 'sem 1', '1']:
                fees_to_bill.append(fee)

        elif fee.frequency == FeeStructure.Frequency.ONCE:
            already_billed = InvoiceItem.objects.filter(
                fee_structure=fee,
                invoice__student=student
            ).exists()
            if not already_billed:
                fees_to_bill.append(fee)

        elif fee.frequency == FeeStructure.Frequency.GRADUATION:
            if current_year and current_year.name.lower() in ['year 4', 'year 5', 'final', '4', '5']:
                fees_to_bill.append(fee)

        elif fee.frequency == FeeStructure.Frequency.MONTHLY:
            fees_to_bill.append(fee)

    return fees_to_bill


@login_required
@finance_required
def scholarship_list(request):
    scholarships = Scholarship.objects.select_related(
        'student__user', 'session'
    ).all().order_by('-awarded_date')
    search = request.GET.get('search', '')
    if search:
        scholarships = scholarships.filter(
            Q(student__student_id__icontains=search) |
            Q(student__user__first_name__icontains=search) |
            Q(student__user__last_name__icontains=search) |
            Q(name__icontains=search) |
            Q(sponsor__icontains=search)
        )
    total = scholarships.aggregate(t=Sum('amount'))['t'] or 0
    return render(request, 'finance/scholarship_list.html', {
        'scholarships': scholarships,
        'search': search,
        'total': total,
    })
