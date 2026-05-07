from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class FeeStructure(models.Model):
    """Fee structure for different programmes and levels."""

    class FeeType(models.TextChoices):
        TUITION = 'tuition', 'Tuition'
        REGISTRATION = 'registration', 'Registration'
        LIBRARY = 'library', 'Library'
        LABORATORY = 'laboratory', 'Laboratory'
        ACCOMMODATION = 'accommodation', 'Accommodation'
        EXAMINATION = 'examination', 'Examination'
        DEVELOPMENT = 'development', 'Development Levy'
        ICT = 'ict', 'ICT Fee'
        MEDICAL = 'medical', 'Medical Fee'
        OTHER = 'other', 'Other'

    class Frequency(models.TextChoices):
        PER_SEMESTER = 'per_semester', 'Per Semester'
        PER_YEAR = 'per_year', 'Per Year'
        ONCE = 'once', 'Once'
        GRADUATION = 'graduation', 'Graduation'
        MONTHLY = 'monthly', 'Monthly'

    name = models.CharField(max_length=100)
    fee_type = models.CharField(max_length=20, choices=FeeType.choices)
    programme = models.ForeignKey(
        'academics.Programme', on_delete=models.CASCADE, null=True, blank=True, related_name='fees'
    )
    level = models.IntegerField(null=True, blank=True, help_text="Specific level or null for all")
    session = models.ForeignKey('academics.AcademicSession', on_delete=models.CASCADE, related_name='fees')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=Frequency.choices, default=Frequency.PER_SEMESTER)
    is_mandatory = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fee_type', 'name']

    def __str__(self):
        return f"{self.name} - {self.amount}"


class StudentFee(models.Model):
    """Fee assignments for individual students."""
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='assigned_fees')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='student_assignments')
    session = models.ForeignKey('academics.AcademicSession', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    assigned_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['student', 'fee_structure', 'session']
        ordering = ['-assigned_date']

    def __str__(self):
        return f"{self.student} - {self.fee_structure.name}"


class Invoice(models.Model):
    """Student billing invoice."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PARTIALLY_PAID = 'partial', 'Partially Paid'
        PAID = 'paid', 'Fully Paid'
        OVERDUE = 'overdue', 'Overdue'
        CANCELLED = 'cancelled', 'Cancelled'

    invoice_number = models.CharField(max_length=30, unique=True)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='invoices')
    session = models.ForeignKey('academics.AcademicSession', on_delete=models.CASCADE)
    semester = models.ForeignKey('academics.StudySemester', on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    due_date = models.DateField(null=True, blank=True)
    issued_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.invoice_number} - {self.student}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
        self.balance = self.total_amount - self.amount_paid
        if self.amount_paid >= self.total_amount:
            self.status = self.Status.PAID
        elif self.amount_paid > 0:
            self.status = self.Status.PARTIALLY_PAID
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    """Individual line items on an invoice."""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.description} - {self.amount}"


class Payment(models.Model):
    """Payment records."""

    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'Cash'
        BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
        CARD = 'card', 'Card Payment'
        MOBILE_MONEY = 'mobile_money', 'Mobile Money'
        CHEQUE = 'cheque', 'Cheque'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'

    receipt_number = models.CharField(max_length=30, unique=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    reference_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    payment_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.receipt_number} - {self.amount}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = f"RCP-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
        if self.status == self.Status.COMPLETED:
            self.invoice.amount_paid = sum(
                p.amount for p in self.invoice.payments.filter(status='completed')
            )
            self.invoice.save()


class Scholarship(models.Model):
    """Scholarship/financial aid records."""
    name = models.CharField(max_length=200)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='scholarships')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    session = models.ForeignKey('academics.AcademicSession', on_delete=models.CASCADE)
    sponsor = models.CharField(max_length=200, blank=True)
    criteria = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    awarded_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.name} - {self.student} ({self.amount})"
