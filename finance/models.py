from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class FeeStructure(models.Model):
    """Fee structure for different programmes, faculties, levels and schedules."""

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
        ORIENTATION = 'orientation', 'Orientation Fee'
        SPORTS = 'sports', 'Sports Fee'
        UNION = 'union', 'Student Union Fee'
        INTERNET = 'internet', 'Internet Access Fee'
        SECURITY = 'security', 'Security Levy'
        INSURANCE = 'insurance', 'Insurance Fee'
        TRANSCRIPT = 'transcript', 'Transcript Fee'
        GRADUATION = 'graduation', 'Graduation Fee'
        RESEARCH = 'research', 'Research/Thesis Fee'
        OTHER = 'other', 'Other'

    class Frequency(models.TextChoices):
        PER_SEMESTER = 'per_semester', 'Per Semester'
        PER_YEAR = 'per_year', 'Per Year'
        ONCE = 'once', 'Once'
        GRADUATION = 'graduation', 'Graduation'
        MONTHLY = 'monthly', 'Monthly'

    class Schedule(models.TextChoices):
        FULLTIME = 'fulltime', 'Full-time'
        WEEKEND = 'weekend', 'Weekend'
        EVENING = 'evening', 'Evening'
        ONLINE = 'online', 'Online'
        HOLIDAY = 'holiday', 'Holiday'
        ALL = 'all', 'All Schedules'

    name = models.CharField(max_length=100)
    fee_type = models.CharField(max_length=20, choices=FeeType.choices)

    # Multiple programmes can be assigned (blank = all programmes)
    programmes = models.ManyToManyField(
        'academics.Programme', blank=True, related_name='fees',
        help_text="Leave empty to apply to all programmes"
    )

    # Multiple faculties can be assigned (blank = all faculties)
    faculties = models.ManyToManyField(
        'academics.Faculty', blank=True, related_name='fees',
        help_text="Leave empty to apply to all faculties"
    )

    # Multiple departments can be assigned (blank = all departments)
    departments = models.ManyToManyField(
        'academics.Department', blank=True, related_name='fees',
        help_text="Leave empty to apply to all departments"
    )

    # Multiple courses can be assigned (blank = all courses)
    courses = models.ManyToManyField(
        'academics.Course', blank=True, related_name='fees',
        help_text="Leave empty to apply to all courses"
    )

    # Schedule options (blank = all schedules)
    schedules = models.JSONField(
        default=list, blank=True,
        help_text="List of schedules this fee applies to (e.g., ['fulltime', 'weekend']). Leave empty for all."
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
        verbose_name = 'Fee Structure'
        verbose_name_plural = 'Fee Structures'

    def __str__(self):
        return f"{self.name} - {self.amount}"

    def get_applicable_programmes(self):
        """Return list of applicable programmes or 'All Programmes'."""
        if self.programmes.exists():
            return ", ".join([p.name for p in self.programmes.all()[:3]])
        return "All Programmes"

    def get_applicable_faculties(self):
        """Return list of applicable faculties or 'All Faculties'."""
        if self.faculties.exists():
            return ", ".join([f.name for f in self.faculties.all()[:3]])
        return "All Faculties"

    def get_applicable_schedules(self):
        """Return list of applicable schedules or 'All Schedules'."""
        if self.schedules:
            schedule_labels = []
            for sched in self.schedules:
                for choice_val, choice_label in self.Schedule.choices:
                    if choice_val == sched:
                        schedule_labels.append(choice_label)
                        break
            return ", ".join(schedule_labels[:3]) if schedule_labels else "All Schedules"
        return "All Schedules"

    def applies_to_student(self, student):
        """Check if this fee applies to a given student."""
        # Check programme
        if self.programmes.exists() and student.programme not in self.programmes.all():
            return False

        # Check faculty
        if self.faculties.exists():
            if not student.programme or not student.programme.department:
                return False
            if student.programme.department.faculty not in self.faculties.all():
                return False

        # Check schedule
        if self.schedules:
            student_schedule = student.programme.schedule
            if student_schedule not in self.schedules:
                return False

        # Check level
        if self.level is not None and student.level != self.level:
            return False

        return True


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
    
    def get_status_color(self):
        colors = {
            'pending': 'warning',
            'partial': 'info',
            'paid': 'success',
            'overdue': 'danger',
            'cancelled': 'secondary'
        }
        return colors.get(self.status, 'secondary')


class InvoiceItem(models.Model):
    """Individual line items on an invoice."""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.description} - {self.amount}"


class Currency(models.Model):
    """Currency model for multi-currency support."""
    code = models.CharField(max_length=3, unique=True)  # USD, EUR, UGX, etc.
    name = models.CharField(max_length=50)  # US Dollar, Euro, Ugandan Shilling
    symbol = models.CharField(max_length=5)  # $, €, UGX
    is_default = models.BooleanField(default=False)
    exchange_rate_to_default = models.DecimalField(max_digits=10, decimal_places=4, default=1.0000)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Currencies"
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        # Ensure only one default currency
        if self.is_default:
            Currency.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_default(cls):
        return cls.objects.filter(is_default=True, is_active=True).first() or cls.objects.filter(code='UGX').first()


class StudentCurrency(models.Model):
    """Student-specific currency preference."""
    student = models.OneToOneField('students.Student', on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Student Currencies"

    def __str__(self):
        return f"{self.student} - {self.currency.code}"


class ProgrammeCurrency(models.Model):
    """Programme-specific currency preference."""
    programme = models.OneToOneField('academics.Programme', on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Programme Currencies"

    def __str__(self):
        return f"{self.programme.name} - {self.currency.code}"

    @classmethod
    def get_currency_for_student(cls, student):
        # Check if student has specific currency
        student_currency = StudentCurrency.objects.filter(student=student).first()
        if student_currency:
            return student_currency.currency
        
        # Check if programme has specific currency
        programme_currency = cls.objects.filter(programme=student.programme).first()
        if programme_currency:
            return programme_currency.currency
        
        # Return default currency
        return Currency.get_default()


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
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, null=True, blank=True)
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
    
    def get_status_color(self):
        colors = {
            'pending': 'warning',
            'completed': 'success',
            'failed': 'danger',
            'refunded': 'secondary'
        }
        return colors.get(self.status, 'secondary')


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


class PaymentItem(models.Model):
    """Track payments allocated to specific invoice items."""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='payment_items')
    invoice_item = models.ForeignKey(InvoiceItem, on_delete=models.CASCADE, related_name='payment_items')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['payment', 'invoice_item']

    def __str__(self):
        return f"{self.payment.receipt_number} - {self.invoice_item.description} ({self.amount})"
