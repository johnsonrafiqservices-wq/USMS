from django.db.models import Sum, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import get_user_model
from accounts.decorators import finance_required
from .models import Invoice, InvoiceItem, Payment, PaymentItem, FeeStructure, Scholarship


@login_required
@finance_required
def student_payment_history(request, student_id):
    from students.models import Student
    from academics.models import AcademicSession, StudySemester, StudyYear
    from django.http import JsonResponse
    from datetime import datetime
    from django.db.models import Q
    student = get_object_or_404(Student, pk=student_id)
    
    invoices = Invoice.objects.filter(student=student).select_related('session', 'semester').order_by('-issued_date')
    payments = Payment.objects.filter(invoice__student=student).select_related('invoice', 'processed_by').order_by('-payment_date')
    
    # Filters
    year_filter = request.GET.get('year')
    semester_filter = request.GET.get('semester')
    fee_type_filter = request.GET.get('fee_type')
    frequency_filter = request.GET.get('frequency')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status_filter = request.GET.get('status')
    
    # Apply filters to invoices
    if year_filter:
        invoices = invoices.filter(session__year=year_filter)
        payments = payments.filter(invoice__session__year=year_filter)
    if semester_filter:
        invoices = invoices.filter(semester_id=semester_filter)
        payments = payments.filter(invoice__semester_id=semester_filter)
    if fee_type_filter:
        payments = payments.filter(paymentitem__fee_structure__fee_type=fee_type_filter)
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            invoices = invoices.filter(issued_date__gte=date_from_obj)
            payments = payments.filter(payment_date__gte=date_from_obj)
        except ValueError:
            pass
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            invoices = invoices.filter(issued_date__lte=date_to_obj)
            payments = payments.filter(payment_date__lte=date_to_obj)
        except ValueError:
            pass
    
    sessions = AcademicSession.objects.all()
    semesters = StudySemester.objects.all()
    years = StudyYear.objects.all()
    
    # Calculate totals
    total_billed = sum(inv.total_amount for inv in invoices)
    total_paid = sum(pay.amount for pay in payments)
    total_balance = sum(inv.balance for inv in invoices)
    
    # Calculate invoiced fees with payment history
    invoiced_fees = []
    fee_payment_history = {}
    
    # Get all invoice items for this student
    base_invoice_items = InvoiceItem.objects.filter(
        invoice__student=student
    ).select_related('invoice', 'fee_structure', 'invoice__session', 'invoice__semester')
    
    # Apply filters at invoice level
    # since fees are linked to invoices through invoice items
    invoice_items = base_invoice_items
    
    # Only apply filters if they have values
    if year_filter:
        invoice_items = invoice_items.filter(invoice__session__year_id=year_filter)
    if semester_filter:
        invoice_items = invoice_items.filter(invoice__semester_id=semester_filter)
    if status_filter:
        invoice_items = invoice_items.filter(invoice__status=status_filter)
    if fee_type_filter:
        invoice_items = invoice_items.filter(fee_structure__fee_type=fee_type_filter)
    if frequency_filter:
        invoice_items = invoice_items.filter(fee_structure__frequency=frequency_filter)
    
    # If no filters are selected, show nothing
    if not year_filter and not semester_filter and not status_filter and not fee_type_filter and not frequency_filter:
        invoiced_fees = []
        fee_payment_history = {}
    else:
        # Group by fee structure to avoid duplicates
        processed_fees = {}
        
        for item in invoice_items:
            fee = item.fee_structure
            fee_key = f"{fee.id}_{fee.fee_type}"
            
            if fee_key not in processed_fees:
                # Calculate total paid for this fee
                paid_amount = 0
                related_invoice = item.invoice
                
                # Get all payments for this fee across all invoice items
                fee_payment_items = PaymentItem.objects.filter(
                    invoice_item__fee_structure=fee,
                    invoice_item__invoice__student=student
                ).select_related('payment', 'payment__processed_by')
                
                for payment_item in fee_payment_items:
                    paid_amount += payment_item.amount
                
                balance = fee.amount - paid_amount
                
                processed_fees[fee_key] = {
                    'fee': fee,
                    'fee_type': fee.get_fee_type_display(),
                    'frequency': fee.get_frequency_display(),
                    'description': fee.description or fee.name,
                    'amount': fee.amount,
                    'paid_amount': paid_amount,
                    'balance': balance,
                    'invoice_number': related_invoice.invoice_number if related_invoice else None,
                }
                
                # Group payments by fee type
                fee_type_key = fee.get_fee_type_display()
                if fee_type_key not in fee_payment_history:
                    fee_payment_history[fee_type_key] = []
                
                # Add payments to history
                for payment_item in fee_payment_items:
                    if payment_item.payment not in fee_payment_history[fee_type_key]:
                        fee_payment_history[fee_type_key].append(payment_item.payment)
        
        # Convert to list and sort
        invoiced_fees = list(processed_fees.values())
        for fee_type_key in fee_payment_history:
            fee_payment_history[fee_type_key].sort(key=lambda x: x.payment_date, reverse=True)
    
    # Handle AJAX request
    if request.GET.get('ajax') == '1':
        tab = request.GET.get('tab')
        print(f"AJAX request for tab: {tab}")
        print(f"Invoices count: {invoices.count()}")
        print(f"Payments count: {payments.count()}")
        
        if tab == 'invoices':
            return render(request, 'finance/partials/invoices_table.html', {
                'invoices': invoices,
            })
        elif tab == 'payments':
            return render(request, 'finance/partials/payments_table.html', {
                'payments': payments,
            })
        elif tab == 'invoiced-fees':
            return render(request, 'finance/partials/invoiced_fees_table.html', {
                'invoiced_fees': invoiced_fees,
            })
        return JsonResponse({'status': 'error', 'message': f'Unknown tab: {tab}'})
    
    return render(request, 'finance/student_payment_history.html', {
        'student': student,
        'invoices': invoices,
        'payments': payments,
        'sessions': sessions,
        'semesters': semesters,
        'years': years,
        'year_filter': year_filter,
        'semester_filter': semester_filter,
        'fee_type_filter': fee_type_filter,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'total_billed': total_billed,
        'total_paid': total_paid,
        'total_balance': total_balance,
        'invoiced_fees': invoiced_fees,
        'fee_payment_history': fee_payment_history,
    })


@login_required
@finance_required
def finance_students(request):
    from students.models import Student
    from academics.models import StudyYear, StudySemester
    from academics.models import Programme, Intake
    from django.db.models import Sum, Count
    
    # Use Sum with distinct=True to avoid double-counting
    students = Student.objects.select_related('user', 'programme', 'current_year', 'current_semester_number', 'intake').filter(
        status__in=['active', 'admitted']
    ).annotate(
        total_billed=Sum('invoices__total_amount', distinct=True),
        total_paid=Sum('invoices__amount_paid', distinct=True),
        total_balance=Sum('invoices__balance', distinct=True),
        invoice_count=Count('invoices', distinct=True),
        payment_count=Count('payments', distinct=True)
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
    # Get filter parameters
    faculty_filter = request.GET.get('faculty', '')
    department_filter = request.GET.get('department', '')
    program_filter = request.GET.get('program', '')
    session_filter = request.GET.get('session', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base querysets with filters
    invoices_query = Invoice.objects.select_related('student__user', 'session', 'semester', 'student__programme')
    payments_query = Payment.objects.select_related('student__user', 'invoice', 'student__programme')
    
    # Apply filters to invoices
    if faculty_filter:
        invoices_query = invoices_query.filter(student__programme__department__faculty_id=faculty_filter)
    if department_filter:
        invoices_query = invoices_query.filter(student__programme__department_id=department_filter)
    if program_filter:
        invoices_query = invoices_query.filter(student__programme_id=program_filter)
    if session_filter:
        invoices_query = invoices_query.filter(session_id=session_filter)
    if date_from:
        invoices_query = invoices_query.filter(issued_date__gte=date_from)
    if date_to:
        invoices_query = invoices_query.filter(issued_date__lte=date_to)
    
    # Apply filters to payments
    if faculty_filter:
        payments_query = payments_query.filter(student__programme__department__faculty_id=faculty_filter)
    if department_filter:
        payments_query = payments_query.filter(student__programme__department_id=department_filter)
    if program_filter:
        payments_query = payments_query.filter(student__programme_id=program_filter)
    if session_filter:
        payments_query = payments_query.filter(invoice__session_id=session_filter)
    if date_from:
        payments_query = payments_query.filter(payment_date__gte=date_from)
    if date_to:
        payments_query = payments_query.filter(payment_date__lte=date_to)
    
    # Calculate totals with filters
    total_revenue = payments_query.filter(status='completed').aggregate(
        total=Sum('amount'))['total'] or 0
    pending_invoices = invoices_query.filter(status='pending').count()
    overdue_invoices = invoices_query.filter(status='overdue').count()
    partial_invoices = invoices_query.filter(status='partial').count()
    total_outstanding = invoices_query.filter(
        status__in=['pending', 'partial', 'overdue']
    ).aggregate(total=Sum('balance'))['total'] or 0
    total_invoiced = invoices_query.aggregate(total=Sum('total_amount'))['total'] or 0
    collection_rate = round((float(total_revenue) / float(total_invoiced) * 100), 1) if total_invoiced else 0

    recent_payments = payments_query.filter(
        status='completed'
    ).order_by('-payment_date')[:10]

    overdue_list = invoices_query.filter(
        status='overdue'
    ).order_by('-balance')[:8]

    # Monthly revenue for current year (last 6 months)
    import json
    from dateutil.relativedelta import relativedelta
    months_data = []
    today = date.today()
    for i in range(5, -1, -1):
        m = today - relativedelta(months=i)
        rev = payments_query.filter(
            status='completed',
            payment_date__year=m.year,
            payment_date__month=m.month,
        ).aggregate(total=Sum('amount'))['total'] or 0
        months_data.append({'label': m.strftime('%b %Y'), 'value': float(rev)})

    scholarships_query = Scholarship.objects.select_related('student__programme')
    if faculty_filter:
        scholarships_query = scholarships_query.filter(student__programme__department__faculty_id=faculty_filter)
    if department_filter:
        scholarships_query = scholarships_query.filter(student__programme__department_id=department_filter)
    if program_filter:
        scholarships_query = scholarships_query.filter(student__programme_id=program_filter)
    if session_filter:
        scholarships_query = scholarships_query.filter(session_id=session_filter)
    if date_from:
        scholarships_query = scholarships_query.filter(awarded_date__gte=date_from)
    if date_to:
        scholarships_query = scholarships_query.filter(awarded_date__lte=date_to)
    
    scholarships_count = scholarships_query.filter(is_active=True).count()
    scholarships_total = scholarships_query.filter(is_active=True).aggregate(
        total=Sum('amount'))['total'] or 0

    # Get filter options
    from academics.models import Faculty, Department, Programme, AcademicSession, Intake
    faculties = Faculty.objects.all()
    departments = Department.objects.all()
    programmes = Programme.objects.all()
    sessions = AcademicSession.objects.all().order_by('-id')
    intakes = Intake.objects.all()

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
        'invoices': invoices_query,
        'payments': payments_query,
        'faculties': faculties,
        'departments': departments,
        'programmes': programmes,
        'sessions': sessions,
        'intakes': intakes,
    })


@login_required
@finance_required
def invoice_list(request):
    invoices = Invoice.objects.select_related('student__user', 'session', 'semester').all()
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    session_filter = request.GET.get('session', '')
    faculty_filter = request.GET.get('faculty', '')
    department_filter = request.GET.get('department', '')
    programme_filter = request.GET.get('programme', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    weekend_filter = request.GET.get('weekend', '')

    # Apply filters
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
    if faculty_filter:
        invoices = invoices.filter(student__programme__department__faculty_id=faculty_filter)
    if department_filter:
        invoices = invoices.filter(student__programme__department_id=department_filter)
    if programme_filter:
        invoices = invoices.filter(student__programme_id=programme_filter)
    if date_from:
        invoices = invoices.filter(issued_date__gte=date_from)
    if date_to:
        invoices = invoices.filter(issued_date__lte=date_to)
    if weekend_filter:
        if weekend_filter == 'yes':
            # Filter invoices issued on weekends (Saturday=6, Sunday=7)
            invoices = invoices.filter(
                Q(issued_date__week_day=6) | Q(issued_date__week_day=7)
            )
        elif weekend_filter == 'no':
            # Filter invoices issued on weekdays (Monday=1 to Friday=5)
            invoices = invoices.filter(
                issued_date__week_day__in=[1, 2, 3, 4, 5]
            )

    # Get filter options
    from academics.models import AcademicSession, Faculty, Department, Programme
    sessions = AcademicSession.objects.all().order_by('-id')
    faculties = Faculty.objects.all()
    departments = Department.objects.all()
    programmes = Programme.objects.all()

    total_amount = invoices.aggregate(t=Sum('total_amount'))['t'] or 0
    total_balance = invoices.aggregate(t=Sum('balance'))['t'] or 0

    return render(request, 'finance/invoice_list.html', {
        'invoices': invoices,
        'statuses': Invoice.Status.choices,
        'sessions': sessions,
        'faculties': faculties,
        'departments': departments,
        'programmes': programmes,
        'status_filter': status_filter,
        'search': search,
        'session_filter': session_filter,
        'faculty_filter': faculty_filter,
        'department_filter': department_filter,
        'programme_filter': programme_filter,
        'date_from': date_from,
        'date_to': date_to,
        'weekend_filter': weekend_filter,
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
    items = invoice.items.select_related('fee_structure').prefetch_related('payment_items__payment')
    payments = invoice.payments.select_related('processed_by').prefetch_related('payment_items__invoice_item').order_by('-payment_date')
    
    # Calculate paid amount and balance for each item
    for item in items:
        item.paid_amount = sum(payment_item.amount for payment_item in item.payment_items.all())
        item.balance_amount = float(item.amount) - float(item.paid_amount)
    
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
        Invoice.objects.select_related('student__user', 'session').prefetch_related('items'),
        pk=invoice_id
    )
    if request.method == 'POST':
        amount = request.POST.get('amount')
        method = request.POST.get('payment_method')
        reference = request.POST.get('reference_number', '')
        notes = request.POST.get('notes', '')
        selected_items = request.POST.getlist('selected_items')
        currency_id = request.POST.get('currency')
        
        # Validate that at least one item is selected
        if not selected_items:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Please select at least one fee item to pay for.'})
            messages.error(request, 'Please select at least one fee item to pay for.')
            return render(request, 'finance/record_payment.html', {
                'invoice': invoice,
                'items': invoice.items.all(),
                'methods': Payment.PaymentMethod.choices,
            })
        
        # Get per-item payment amounts
        item_payments = {}
        total_calculated = 0
        
        for item_id in selected_items:
            pay_amount_key = f'pay_amount_{item_id}'
            pay_amount = request.POST.get(pay_amount_key, '0')
            
            try:
                pay_amount_float = float(pay_amount)
                if pay_amount_float > 0:
                    item_payments[item_id] = pay_amount_float
                    total_calculated += pay_amount_float
            except (ValueError, TypeError):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': f'Invalid payment amount for item {item_id}.'})
                messages.error(request, f'Invalid payment amount for item {item_id}.')
                return render(request, 'finance/record_payment.html', {
                    'invoice': invoice,
                    'items': invoice.items.all(),
                    'methods': Payment.PaymentMethod.choices,
                })
        
        if not item_payments:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Please enter payment amounts for at least one selected item.'})
            messages.error(request, 'Please enter payment amounts for at least one selected item.')
            return render(request, 'finance/record_payment.html', {
                'invoice': invoice,
                'items': invoice.items.all(),
                'methods': Payment.PaymentMethod.choices,
            })
        
        try:
            amt = float(amount)
            if amt <= 0:
                raise ValueError
        except (ValueError, TypeError):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Enter a valid positive amount.'})
            messages.error(request, 'Enter a valid positive amount.')
            return render(request, 'finance/record_payment.html', {
                'invoice': invoice,
                'items': invoice.items.all(),
                'methods': Payment.PaymentMethod.choices,
            })

        # Validate that total matches calculated amount
        if abs(amt - total_calculated) > 0.01:  # Allow for small floating point differences
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': f'Total payment amount (UGX {amt:,.0f}) must match the sum of item payments (UGX {total_calculated:,.0f}).'})
            messages.error(request, f'Total payment amount (UGX {amt:,.0f}) must match the sum of item payments (UGX {total_calculated:,.0f}).')
            return render(request, 'finance/record_payment.html', {
                'invoice': invoice,
                'items': invoice.items.all(),
                'methods': Payment.PaymentMethod.choices,
            })

        # Create payment with selected items info in notes
        items_paid_info = []
        for item_id, pay_amount in item_payments.items():
            item = invoice.items.get(pk=item_id)
            items_paid_info.append(f"{item.description}: UGX {pay_amount:,.0f}")
        
        items_info = ", ".join(items_paid_info)
        payment_notes = f"{notes}\n\nFee items paid: {items_info}" if notes else f"Fee items paid: {items_info}"
        
        # Get currency
        from .models import Currency, ProgrammeCurrency
        currency = Currency.objects.get(pk=currency_id) if currency_id else Currency.get_default()
        
        payment = Payment.objects.create(
            invoice=invoice,
            student=invoice.student,
            amount=amt,
            currency=currency,
            payment_method=method,
            reference_number=reference,
            notes=payment_notes,
            status='completed',
            processed_by=request.user,
        )
        
        # Create PaymentItem records for each paid invoice item
        for item_id, pay_amount in item_payments.items():
            item = invoice.items.get(pk=item_id)
            PaymentItem.objects.create(
                payment=payment,
                invoice_item=item,
                amount=pay_amount
            )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Payment of UGX {amt:,.0f} recorded for {len(selected_items)} fee item(s). Receipt: {payment.receipt_number}',
                'redirect': f'/finance/invoices/{invoice.pk}/'
            })
        messages.success(
            request,
            f'Payment of UGX {amt:,.0f} recorded for {len(selected_items)} fee item(s). Receipt: {payment.receipt_number}'
        )
        return redirect('finance:invoice_detail', pk=invoice.pk)

    # Get currency options
    from .models import Currency, ProgrammeCurrency
    currencies = Currency.objects.filter(is_active=True).order_by('code')
    
    # Get student's preferred currency
    student_currency = ProgrammeCurrency.get_currency_for_student(invoice.student)
    
    # Calculate remaining balance for each item
    items_with_balance = []
    for item in invoice.items.all().prefetch_related('payment_items'):
        # Sum all payments made for this item
        paid_amount = sum(pi.amount for pi in item.payment_items.all())
        remaining_balance = item.amount - paid_amount
        if remaining_balance < 0:
            remaining_balance = 0
        
        # Add balance attribute to item
        item.balance = remaining_balance
        items_with_balance.append(item)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'finance/record_payment_fragment.html', {
            'invoice': invoice,
            'items': items_with_balance,
            'methods': Payment.PaymentMethod.choices,
            'currencies': currencies,
            'student_currency': student_currency,
        })
    
    return render(request, 'finance/record_payment.html', {
        'invoice': invoice,
        'items': items_with_balance,
        'methods': Payment.PaymentMethod.choices,
        'currencies': currencies,
        'student_currency': student_currency,
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
    from academics.models import AcademicSession, Faculty
    fees = FeeStructure.objects.prefetch_related('programmes', 'faculties').select_related('session').all()
    session_filter = request.GET.get('session', '')
    type_filter = request.GET.get('type', '')
    programme_filter = request.GET.get('programme', '')
    faculty_filter = request.GET.get('faculty', '')
    schedule_filter = request.GET.get('schedule', '')
    sessions = AcademicSession.objects.all().order_by('-id')

    if session_filter:
        fees = fees.filter(session_id=session_filter)
    if type_filter:
        fees = fees.filter(fee_type=type_filter)
    if programme_filter:
        fees = fees.filter(programmes__id=programme_filter)
    if faculty_filter:
        fees = fees.filter(faculties__id=faculty_filter)
    if schedule_filter:
        fees = fees.filter(schedules__contains=[schedule_filter])

    from academics.models import Programme
    programmes = Programme.objects.all()
    faculties = Faculty.objects.all()

    return render(request, 'finance/fee_structure.html', {
        'fees': fees,
        'sessions': sessions,
        'programmes': programmes,
        'faculties': faculties,
        'fee_types': FeeStructure.FeeType.choices,
        'schedules': FeeStructure.Schedule.choices,
        'session_filter': session_filter,
        'type_filter': type_filter,
        'programme_filter': programme_filter,
        'faculty_filter': faculty_filter,
        'schedule_filter': schedule_filter,
    })


@login_required
@finance_required
def fee_structure_create(request):
    from academics.models import AcademicSession, Programme, Faculty, Department, Course
    from django.http import JsonResponse
    import json
    sessions = AcademicSession.objects.all().order_by('-id')
    programmes = Programme.objects.select_related('department__faculty').all()
    faculties = Faculty.objects.all()
    departments = Department.objects.select_related('faculty').all()
    courses = Course.objects.select_related('department').all()

    # Create JSON data for programmes with faculty_id for JavaScript filtering
    programmes_json = [
        {'id': p.pk, 'name': p.name, 'faculty_id': p.department.faculty_id}
        for p in programmes
    ]

    # Create JSON data for departments with faculty_id for JavaScript filtering
    departments_json = [
        {'id': d.pk, 'name': d.name, 'faculty_id': d.faculty_id}
        for d in departments
    ]

    # Create JSON data for courses with department_id for JavaScript filtering
    courses_json = [
        {'id': c.pk, 'code': c.code, 'title': c.title, 'department_id': c.department_id}
        for c in courses
    ]

    if request.method == 'POST':
        name = request.POST.get('name')
        fee_type = request.POST.get('fee_type')
        frequency = request.POST.get('frequency', 'per_semester')
        level = request.POST.get('level') or None
        session_id = request.POST.get('session')
        amount = request.POST.get('amount')
        is_mandatory = request.POST.get('is_mandatory') == 'on'
        description = request.POST.get('description', '')

        # Get multiple selections
        programme_ids = request.POST.getlist('programmes')
        faculty_ids = request.POST.getlist('faculties')
        department_ids = request.POST.getlist('departments')
        course_ids = request.POST.getlist('courses')
        schedule_values = request.POST.getlist('schedules')

        if not all([name, fee_type, session_id, amount]):
            return JsonResponse({'success': False, 'message': 'Please fill all required fields.'})

        # Validate amount is a valid number
        try:
            amount_decimal = Decimal(amount)
            if amount_decimal <= 0:
                return JsonResponse({'success': False, 'message': 'Amount must be greater than zero.'})
        except Exception:
            return JsonResponse({'success': False, 'message': 'Please enter a valid amount.'})

        try:
            fee = FeeStructure.objects.create(
                name=name,
                fee_type=fee_type,
                frequency=frequency,
                level=int(level) if level else None,
                session_id=session_id,
                amount=amount_decimal,
                is_mandatory=is_mandatory,
                description=description,
                schedules=schedule_values if schedule_values else [],
            )

            # Add many-to-many relationships (filter out 'all' value)
            actual_programme_ids = [pid for pid in programme_ids if pid != 'all']
            actual_faculty_ids = [fid for fid in faculty_ids if fid != 'all']
            actual_department_ids = [did for did in department_ids if did != 'all']
            actual_course_ids = [cid for cid in course_ids if cid != 'all']
            if actual_programme_ids:
                fee.programmes.set(actual_programme_ids)
            if actual_faculty_ids:
                fee.faculties.set(actual_faculty_ids)
            if actual_department_ids:
                fee.departments.set(actual_department_ids)
            if actual_course_ids:
                fee.courses.set(actual_course_ids)

            return JsonResponse({
                'success': True,
                'message': f'Fee structure "{fee.name}" created successfully.'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error saving data: {str(e)}'})

    return render(request, 'finance/fee_structure_form_fragment.html', {
        'sessions': sessions,
        'programmes': programmes,
        'faculties': faculties,
        'departments': departments,
        'courses': courses,
        'programmes_json': json.dumps(programmes_json),
        'departments_json': json.dumps(departments_json),
        'courses_json': json.dumps(courses_json),
        'fee_types': FeeStructure.FeeType.choices,
        'schedules': FeeStructure.Schedule.choices,
    })


@login_required
@finance_required
def fee_structure_edit(request, pk):
    from academics.models import AcademicSession, Programme, Faculty, Department, Course
    from django.http import JsonResponse
    import json
    fee = get_object_or_404(FeeStructure.objects.prefetch_related('programmes', 'faculties', 'departments', 'courses'), pk=pk)
    sessions = AcademicSession.objects.all().order_by('-id')
    programmes = Programme.objects.select_related('department__faculty').all()
    faculties = Faculty.objects.all()
    departments = Department.objects.select_related('faculty').all()
    courses = Course.objects.select_related('department').all()

    # Create JSON data for programmes with faculty_id for JavaScript filtering
    programmes_json = [
        {'id': p.pk, 'name': p.name, 'faculty_id': p.department.faculty_id}
        for p in programmes
    ]

    # Create JSON data for departments with faculty_id for JavaScript filtering
    departments_json = [
        {'id': d.pk, 'name': d.name, 'faculty_id': d.faculty_id}
        for d in departments
    ]

    # Create JSON data for courses with department_id for JavaScript filtering
    courses_json = [
        {'id': c.pk, 'code': c.code, 'title': c.title, 'department_id': c.department_id}
        for c in courses
    ]

    if request.method == 'POST':
        name = request.POST.get('name')
        fee_type = request.POST.get('fee_type')
        frequency = request.POST.get('frequency', 'per_semester')
        level = request.POST.get('level') or None
        session_id = request.POST.get('session')
        amount = request.POST.get('amount')
        is_mandatory = request.POST.get('is_mandatory') == 'on'
        description = request.POST.get('description', '')

        # Get multiple selections
        programme_ids = request.POST.getlist('programmes')
        faculty_ids = request.POST.getlist('faculties')
        department_ids = request.POST.getlist('departments')
        course_ids = request.POST.getlist('courses')
        schedule_values = request.POST.getlist('schedules')

        if not all([name, fee_type, session_id, amount]):
            return JsonResponse({'success': False, 'message': 'Please fill all required fields.'})

        # Validate amount is a valid number
        try:
            amount_decimal = Decimal(amount)
            if amount_decimal <= 0:
                return JsonResponse({'success': False, 'message': 'Amount must be greater than zero.'})
        except Exception:
            return JsonResponse({'success': False, 'message': 'Please enter a valid amount.'})

        try:
            fee.name = name
            fee.fee_type = fee_type
            fee.frequency = frequency
            fee.level = int(level) if level else None
            fee.session_id = session_id
            fee.amount = amount_decimal
            fee.is_mandatory = is_mandatory
            fee.description = description
            fee.schedules = schedule_values if schedule_values else []
            fee.save()

            # Update many-to-many relationships (filter out 'all' value)
            actual_programme_ids = [pid for pid in programme_ids if pid != 'all']
            actual_faculty_ids = [fid for fid in faculty_ids if fid != 'all']
            actual_department_ids = [did for did in department_ids if did != 'all']
            actual_course_ids = [cid for cid in course_ids if cid != 'all']
            fee.programmes.set(actual_programme_ids)
            fee.faculties.set(actual_faculty_ids)
            fee.departments.set(actual_department_ids)
            fee.courses.set(actual_course_ids)

            return JsonResponse({
                'success': True,
                'message': f'Fee structure "{fee.name}" updated successfully.'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error saving data: {str(e)}'})

    return render(request, 'finance/fee_structure_form_fragment.html', {
        'fee': fee,
        'sessions': sessions,
        'programmes': programmes,
        'faculties': faculties,
        'departments': departments,
        'courses': courses,
        'programmes_json': json.dumps(programmes_json),
        'departments_json': json.dumps(departments_json),
        'courses_json': json.dumps(courses_json),
        'fee_types': FeeStructure.FeeType.choices,
        'schedules': FeeStructure.Schedule.choices,
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
def fee_structure_detail(request, pk):
    """View details of a specific fee structure."""
    from academics.models import Faculty, Programme, AcademicSession, Intake, StudyYear, StudySemester
    from students.models import Student
    from django.db.models import Q, Count
    import json

    fee = get_object_or_404(
        FeeStructure.objects.prefetch_related('programmes', 'faculties', 'session'),
        pk=pk
    )

    # Get filter parameters for main students tab
    faculty_id = request.GET.get('faculty')
    department_id = request.GET.get('department')
    programme_id = request.GET.get('programme')
    intake_id = request.GET.get('intake')
    session_id = request.GET.get('session')
    
    # Get filter parameters for pending tab
    pending_faculty = request.GET.get('pending_faculty')
    pending_department = request.GET.get('pending_department')
    pending_programme = request.GET.get('pending_programme')
    pending_intake = request.GET.get('pending_intake')
    
    # Get filter parameters for paid tab
    paid_faculty = request.GET.get('paid_faculty')
    paid_department = request.GET.get('paid_department')
    paid_programme = request.GET.get('paid_programme')
    paid_intake = request.GET.get('paid_intake')

    # Get applicable programmes (filtered or all)
    if fee.programmes.exists():
        applicable_programmes = fee.programmes.all()
    else:
        if fee.faculties.exists():
            applicable_programmes = Programme.objects.filter(department__faculty__in=fee.faculties.all())
        else:
            applicable_programmes = Programme.objects.all()

    # Get applicable faculties
    if fee.faculties.exists():
        applicable_faculties = fee.faculties.all()
    else:
        applicable_faculties = Faculty.objects.all()

    # Find students affected by this fee
    students_query = Student.objects.all().select_related('user', 'programme', 'programme__department__faculty', 'intake')

    # Apply fee filters - only if they would match some students
    if fee.programmes.exists():
        programme_students = students_query.filter(programme__in=fee.programmes.all())
        if programme_students.exists():
            students_query = programme_students
    elif fee.faculties.exists():
        faculty_students = students_query.filter(programme__department__faculty__in=fee.faculties.all())
        if faculty_students.exists():
            students_query = faculty_students

    if fee.level:
        level_students = students_query.filter(current_year_id=fee.level)
        if level_students.exists():
            students_query = level_students

    # Apply additional filters from form
    if faculty_id:
        students_query = students_query.filter(programme__department__faculty_id=faculty_id)
    if department_id:
        students_query = students_query.filter(programme__department_id=department_id)
    if programme_id:
        students_query = students_query.filter(programme_id=programme_id)
    if intake_id:
        students_query = students_query.filter(intake_id=intake_id)
    if session_id:
        # Filter students by session using available relationships
        try:
            # Get student IDs from enrollments through academic year enrollments
            # This approach works with available model fields
            enrolled_student_ids = Enrollment.objects.filter(
                academic_year_enrollment__session_id=session_id
            ).values_list('student_id', flat=True).distinct()
            
            # Filter main query to only include these students
            students_query = students_query.filter(id__in=enrolled_student_ids)
        except Exception:
            # If session filtering fails, skip it to avoid breaking other filters
            pass

    # Get counts
    total_students = students_query.count()
    active_students = students_query.filter(status='active').count()
    total_programmes = applicable_programmes.count()
    total_faculties = applicable_faculties.count()

    # Prepare student data with payment information
    affected_students_data = []
    pending_students = []
    paid_students = []
    pending_count = 0
    paid_count = 0
    
    for student in students_query[:100]:  # Limit to 100 for performance
        # Find invoices for this student that include this fee
        student_invoices = Invoice.objects.filter(
            student=student,
            items__fee_structure=fee
        ).distinct()
        
        payment_status = 'Not Invoiced'
        balance = fee.amount
        amount_paid = 0
        payment_date = None
        
        if student_invoices.exists():
            # Get the latest invoice
            latest_invoice = student_invoices.order_by('-created_at').first()
            # Calculate total amount for this specific fee
            fee_items = latest_invoice.items.filter(fee_structure=fee)
            total_fee_amount = sum(item.amount for item in fee_items)
            
            # Get exact amount paid for this fee using PaymentItem
            from .models import PaymentItem
            fee_item_ids = [item.id for item in fee_items]
            payment_items = PaymentItem.objects.filter(
                invoice_item_id__in=fee_item_ids
            ).select_related('payment')
            
            # Sum exact payments for this fee
            amount_paid = sum(pi.amount for pi in payment_items)
            
            # Get the latest payment date for this fee
            latest_payment_item = payment_items.order_by('-payment__payment_date').first()
            if latest_payment_item:
                payment_date = latest_payment_item.payment.payment_date
            
            balance = total_fee_amount - amount_paid
            
            if amount_paid >= total_fee_amount:
                payment_status = 'Paid'
            elif amount_paid > 0:
                payment_status = 'Partially Paid'
            else:
                payment_status = 'Pending'
        
        student_data = {
            'student': student,
            'payment_status': payment_status,
            'balance': balance,
            'amount_paid': amount_paid,
            'fee_amount': fee.amount,
            'payment_date': payment_date
        }
        
        affected_students_data.append(student_data)
        
        # Separate into pending and paid lists
        if payment_status in ['Pending', 'Partially Paid', 'Not Invoiced']:
            pending_students.append(student_data)
        elif payment_status == 'Paid':
            paid_students.append(student_data)
    
    # Apply pending tab filters
    if pending_faculty:
        pending_students = [s for s in pending_students if s['student'].programme.department.faculty_id == int(pending_faculty)]
    if pending_department:
        pending_students = [s for s in pending_students if s['student'].programme.department_id == int(pending_department)]
    if pending_programme:
        pending_students = [s for s in pending_students if s['student'].programme_id == int(pending_programme)]
    if pending_intake:
        pending_students = [s for s in pending_students if s['student'].intake_id == int(pending_intake)]
    
    # Apply paid tab filters
    if paid_faculty:
        paid_students = [s for s in paid_students if s['student'].programme.department.faculty_id == int(paid_faculty)]
    if paid_department:
        paid_students = [s for s in paid_students if s['student'].programme.department_id == int(paid_department)]
    if paid_programme:
        paid_students = [s for s in paid_students if s['student'].programme_id == int(paid_programme)]
    if paid_intake:
        paid_students = [s for s in paid_students if s['student'].intake_id == int(paid_intake)]
    
    # Update counts after filtering
    pending_count = len(pending_students)
    paid_count = len(paid_students)

    # Prepare programmes data for JavaScript
    programmes_json = []
    for programme in Programme.objects.all().select_related('department__faculty'):
        programmes_json.append({
            'id': programme.pk,
            'name': programme.name,
            'department__id': programme.department_id,
            'department__name': programme.department.name,
            'department__faculty__id': programme.department.faculty_id,
            'department__faculty__name': programme.department.faculty.name
        })

    return render(request, 'finance/fee_structure_detail.html', {
        'fee': fee,
        'all_programmes': Programme.objects.all(),
        'all_faculties': Faculty.objects.all(),
        'applicable_programmes': applicable_programmes,
        'applicable_faculties': applicable_faculties,
        'affected_students_data': affected_students_data,
        'total_students': total_students,
        'active_students': active_students,
        'total_programmes': total_programmes,
        'total_faculties': total_faculties,
        'intakes': Intake.objects.all(),
        'sessions': AcademicSession.objects.all(),
        'programmes_json': json.dumps(programmes_json),
        'pending_students': pending_students,
        'paid_students': paid_students,
        'pending_count': pending_count,
        'paid_count': paid_count,
    })


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

                # Generate invoices for all students, even without assigned fees
                fees_to_bill = _get_fees_to_bill(assigned_fees, student, semester, session)

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


def _get_fees_to_bill(assigned_fees, student, semester, session):
    """Determine which fees should be billed based on frequency and automatically include all applicable fees."""
    fees_to_bill = []
    current_year = student.current_year
    current_semester = student.current_semester_number

    # Get all applicable fees for this student's programme and year
    all_applicable_fees = FeeStructure.objects.filter(
        Q(programme=student.programme) | Q(programme__isnull=True)
    ).filter(
            Q(level=current_year) | Q(level__isnull=True)
        )

    # Process each applicable fee
    for fee in all_applicable_fees:
        # Skip if already assigned (avoid duplicates)
        if fee in [assignment.fee_structure for assignment in assigned_fees]:
            continue

        if fee.frequency == FeeStructure.Frequency.PER_SEMESTER:
            # Always include semester fees for the current semester
            fees_to_bill.append(fee)

        elif fee.frequency == FeeStructure.Frequency.PER_YEAR:
            # Include yearly fees in semester 1 only
            if current_semester and current_semester.name.lower() in ['semester 1', 'sem 1', '1']:
                fees_to_bill.append(fee)

        elif fee.frequency == FeeStructure.Frequency.ONCE:
            # Include one-time fees if not already billed
            already_billed = InvoiceItem.objects.filter(
                fee_structure=fee,
                invoice__student=student
            ).exists()
            if not already_billed:
                fees_to_bill.append(fee)

        elif fee.frequency == FeeStructure.Frequency.GRADUATION:
            # Include graduation fees in final years
            if current_year and current_year.name.lower() in ['year 4', 'year 5', 'final', '4', '5']:
                fees_to_bill.append(fee)

        elif fee.frequency == FeeStructure.Frequency.MONTHLY:
            # Always include monthly fees
            fees_to_bill.append(fee)

    # Also process explicitly assigned fees
    for assignment in assigned_fees:
        fee = assignment.fee_structure

        if fee.programme and fee.programme != student.programme:
            continue

        if fee.level and fee.level != current_year:
            continue

        # Skip if already added above
        if fee in fees_to_bill:
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
def transaction_list(request):
    from academics.models import AcademicSession, StudySemester
    from students.models import Student
    from django.core.paginator import Paginator
    
    # Get all transactions (invoices and payments)
    invoices = Invoice.objects.select_related('student__user', 'session', 'semester').all()
    payments = Payment.objects.select_related('student__user', 'invoice').all()
    
    # Filters
    search = request.GET.get('search', '')
    transaction_type = request.GET.get('type', '')
    session_filter = request.GET.get('session', '')
    semester_filter = request.GET.get('semester', '')
    status_filter = request.GET.get('status', '')
    method_filter = request.GET.get('method', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Apply filters to invoices
    if search:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search) |
            Q(student__student_id__icontains=search) |
            Q(student__user__first_name__icontains=search) |
            Q(student__user__last_name__icontains=search)
        )
    if session_filter:
        invoices = invoices.filter(session_id=session_filter)
    if semester_filter:
        invoices = invoices.filter(semester_id=semester_filter)
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    if date_from:
        invoices = invoices.filter(issued_date__gte=date_from)
    if date_to:
        invoices = invoices.filter(issued_date__lte=date_to)
    
    # Apply filters to payments
    if search:
        payments = payments.filter(
            Q(receipt_number__icontains=search) |
            Q(student__student_id__icontains=search) |
            Q(student__user__first_name__icontains=search) |
            Q(student__user__last_name__icontains=search) |
            Q(reference_number__icontains=search)
        )
    if session_filter:
        payments = payments.filter(invoice__session_id=session_filter)
    if semester_filter:
        payments = payments.filter(invoice__semester_id=semester_filter)
    if method_filter:
        payments = payments.filter(payment_method=method_filter)
    if date_from:
        payments = payments.filter(payment_date__gte=date_from)
    if date_to:
        payments = payments.filter(payment_date__lte=date_to)
    
    # Filter by transaction type
    if transaction_type == 'invoice':
        payments = Payment.objects.none()
    elif transaction_type == 'payment':
        invoices = Invoice.objects.none()
    
    # Order by date (newest first)
    invoices = invoices.order_by('-issued_date')
    payments = payments.order_by('-payment_date')
    
    # Calculate totals
    total_invoices_amount = invoices.aggregate(t=Sum('total_amount'))['t'] or 0
    total_payments_amount = payments.filter(status='completed').aggregate(t=Sum('amount'))['t'] or 0
    
    # Get filter options
    sessions = AcademicSession.objects.all().order_by('-id')
    semesters = StudySemester.objects.all()
    
    # Pagination
    paginator = Paginator(list(invoices) + list(payments), 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'finance/transaction_list.html', {
        'page_obj': page_obj,
        'invoices': invoices,
        'payments': payments,
        'sessions': sessions,
        'semesters': semesters,
        'search': search,
        'transaction_type': transaction_type,
        'session_filter': session_filter,
        'semester_filter': semester_filter,
        'status_filter': status_filter,
        'method_filter': method_filter,
        'date_from': date_from,
        'date_to': date_to,
        'total_invoices_amount': total_invoices_amount,
        'total_payments_amount': total_payments_amount,
    })


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
