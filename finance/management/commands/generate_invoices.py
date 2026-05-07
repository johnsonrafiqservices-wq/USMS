from django.core.management.base import BaseCommand
from django.utils import timezone
from finance.models import FeeStructure, StudentFee, Invoice, InvoiceItem
from students.models import Student
from academics.models import AcademicSession, StudySemester


class Command(BaseCommand):
    help = 'Generate automatic invoices for students based on their assigned fee structures'

    def add_arguments(self, parser):
        parser.add_argument(
            '--session',
            type=str,
            help='Academic session code (e.g., 2024-2025)',
        )
        parser.add_argument(
            '--semester',
            type=int,
            help='Semester ID',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be invoiced without creating invoices',
        )

    def handle(self, *args, **options):
        session_code = options.get('session')
        semester_id = options.get('semester')
        dry_run = options.get('dry_run', False)

        # Get current session if not specified
        if session_code:
            session = AcademicSession.objects.get(code=session_code)
        else:
            session = AcademicSession.objects.filter(is_current=True).first()
            if not session:
                self.stdout.write(self.style.ERROR('No current session found. Specify --session parameter.'))
                return

        # Get semester if specified
        semester = None
        if semester_id:
            semester = StudySemester.objects.get(pk=semester_id)

        self.stdout.write(f'Generating invoices for session: {session.name}')
        if semester:
            self.stdout.write(f'Semester: {semester.name}')

        # Get all active students
        students = Student.objects.filter(status='active').select_related('user', 'programme', 'current_year', 'current_semester_number')
        self.stdout.write(f'Found {students.count()} active students')

        invoices_created = 0
        total_amount = 0

        for student in students:
            # Get student's assigned fee structures
            assigned_fees = StudentFee.objects.filter(
                student=student,
                session=session,
                is_active=True
            ).select_related('fee_structure')

            if not assigned_fees.exists():
                continue

            # Determine which fees to bill based on frequency
            fees_to_bill = self._get_fees_to_bill(assigned_fees, student, semester)

            if not fees_to_bill:
                continue

            # Calculate total
            total = sum(fee.amount for fee in fees_to_bill)

            if dry_run:
                self.stdout.write(f'[DRY RUN] Student: {student.user.get_full_name()} ({student.student_id})')
                self.stdout.write(f'  Fees: {", ".join([f.name for f in fees_to_bill])}')
                self.stdout.write(f'  Total: UGX {total:,.0f}')
                total_amount += total
                invoices_created += 1
            else:
                # Check if invoice already exists for this student/semester
                existing_invoice = Invoice.objects.filter(
                    student=student,
                    session=session,
                    semester=semester
                ).first()

                if existing_invoice:
                    self.stdout.write(f'Skipping {student.user.get_full_name()} - invoice already exists')
                    continue

                # Create invoice
                invoice = Invoice.objects.create(
                    student=student,
                    session=session,
                    semester=semester,
                    total_amount=total,
                    created_by=None,  # System-generated
                )

                # Create invoice items
                for fee in fees_to_bill:
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        description=f'{fee.name} ({fee.get_frequency_display()})',
                        amount=fee.amount,
                        fee_structure=fee
                    )

                self.stdout.write(f'Created invoice for {student.user.get_full_name()}: UGX {total:,.0f}')
                invoices_created += 1
                total_amount += total

        if dry_run:
            self.stdout.write(self.style.WARNING(f'\n[DRY RUN] Would create {invoices_created} invoices totaling UGX {total_amount:,.0f}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\nCreated {invoices_created} invoices totaling UGX {total_amount:,.0f}'))

    def _get_fees_to_bill(self, assigned_fees, student, semester):
        """Determine which fees should be billed based on frequency."""
        fees_to_bill = []
        current_year = student.current_year
        current_semester = student.current_semester_number

        for assignment in assigned_fees:
            fee = assignment.fee_structure

            # Skip if fee is programme-specific and doesn't match student's programme
            if fee.programme and fee.programme != student.programme:
                continue

            # Skip if fee is level-specific and doesn't match student's current level
            if fee.level and fee.level != current_year:
                continue

            # Apply frequency logic
            if fee.frequency == FeeStructure.Frequency.PER_SEMESTER:
                # Bill every semester
                fees_to_bill.append(fee)

            elif fee.frequency == FeeStructure.Frequency.PER_YEAR:
                # Bill only in semester 1 of each year
                if current_semester and current_semester.name.lower() in ['semester 1', 'sem 1', '1']:
                    fees_to_bill.append(fee)

            elif fee.frequency == FeeStructure.Frequency.ONCE:
                # Check if already billed
                already_billed = InvoiceItem.objects.filter(
                    fee_structure=fee,
                    invoice__student=student
                ).exists()
                if not already_billed:
                    fees_to_bill.append(fee)

            elif fee.frequency == FeeStructure.Frequency.GRADUATION:
                # Only bill in final year
                if current_year and current_year.name.lower() in ['year 4', 'year 5', 'final', '4', '5']:
                    fees_to_bill.append(fee)

            elif fee.frequency == FeeStructure.Frequency.MONTHLY:
                # Bill every semester (simplified - could be enhanced for monthly billing)
                fees_to_bill.append(fee)

        return fees_to_bill
