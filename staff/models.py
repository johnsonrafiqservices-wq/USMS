from django.db import models
from django.conf import settings


class StaffProfile(models.Model):
    """Staff/Lecturer profile."""

    class StaffType(models.TextChoices):
        ACADEMIC = 'academic', 'Academic Staff'
        NON_ACADEMIC = 'non_academic', 'Non-Academic Staff'
        ADMINISTRATIVE = 'administrative', 'Administrative Staff'

    class Rank(models.TextChoices):
        PROFESSOR = 'professor', 'Professor'
        ASSOCIATE_PROF = 'associate_professor', 'Associate Professor'
        SENIOR_LECTURER = 'senior_lecturer', 'Senior Lecturer'
        LECTURER_I = 'lecturer_i', 'Lecturer I'
        LECTURER_II = 'lecturer_ii', 'Lecturer II'
        ASSISTANT_LECTURER = 'assistant_lecturer', 'Assistant Lecturer'
        GRADUATE_ASSISTANT = 'graduate_assistant', 'Graduate Assistant'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='staff_profile')
    staff_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(
        'academics.Department', on_delete=models.SET_NULL, null=True, related_name='staff_members'
    )
    staff_type = models.CharField(max_length=20, choices=StaffType.choices, default=StaffType.ACADEMIC)
    rank = models.CharField(max_length=30, choices=Rank.choices, blank=True)
    qualification = models.CharField(max_length=200, blank=True)
    specialization = models.CharField(max_length=200, blank=True)
    date_employed = models.DateField(null=True, blank=True)
    contract_type = models.CharField(
        max_length=20,
        choices=[('full_time', 'Full Time'), ('part_time', 'Part Time'), ('contract', 'Contract')],
        default='full_time'
    )
    max_workload = models.IntegerField(default=18, help_text="Maximum credit units per semester")
    office_location = models.CharField(max_length=100, blank=True)
    research_interests = models.TextField(blank=True)
    publications = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['staff_id']

    def __str__(self):
        return f"{self.staff_id} - {self.user.get_full_name()}"

    @property
    def current_workload(self):
        """Calculate current semester workload in credit units."""
        from academics.models import CourseAllocation, Semester
        current_sem = Semester.objects.filter(is_current=True).first()
        if not current_sem:
            return 0
        allocations = CourseAllocation.objects.filter(
            lecturer=self, semester=current_sem, is_active=True
        )
        return sum(a.course.credit_units for a in allocations)

    @property
    def workload_percentage(self):
        if self.max_workload == 0:
            return 0
        return round((self.current_workload / self.max_workload) * 100, 1)


class StaffPerformance(models.Model):
    """Track staff performance metrics."""
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='performance_records')
    semester = models.ForeignKey('academics.StudySemester', on_delete=models.CASCADE)
    teaching_score = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    research_score = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    community_score = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overall_rating = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    comments = models.TextField(blank=True)
    evaluated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['staff', 'semester']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.staff} - {self.semester} ({self.overall_rating})"


class Payroll(models.Model):
    """Monthly payroll record for a staff member."""
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        APPROVED = 'approved', 'Approved'
        PAID = 'paid', 'Paid'

    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='payrolls')
    month = models.DateField(help_text="First day of the pay month, e.g. 2025-01-01")
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    housing_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nssf_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='NSSF Deduction')
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    payment_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_payrolls'
    )
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['staff', 'month']
        ordering = ['-month']

    def __str__(self):
        return f"{self.staff} - {self.month.strftime('%B %Y')} ({self.status})"

    def calculate_net(self):
        gross = (self.basic_salary + self.housing_allowance +
                 self.transport_allowance + self.other_allowances)
        deductions = self.tax_deduction + self.nssf_deduction + self.other_deductions
        self.net_pay = gross - deductions
        return self.net_pay

    def save(self, *args, **kwargs):
        self.calculate_net()
        super().save(*args, **kwargs)


class LeaveType(models.Model):
    """Types of staff leave."""
    name = models.CharField(max_length=100)
    max_days_per_year = models.IntegerField(default=21)
    is_paid = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class LeaveRequest(models.Model):
    """Staff leave request."""
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        CANCELLED = 'cancelled', 'Cancelled'

    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_leaves')
    review_remarks = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.staff} - {self.leave_type} ({self.start_date} to {self.end_date})"

    @property
    def days_requested(self):
        return (self.end_date - self.start_date).days + 1


class Document(models.Model):
    """Document management for staff and students."""
    class DocumentType(models.TextChoices):
        CERTIFICATE = 'certificate', 'Certificate'
        TRANSCRIPT = 'transcript', 'Transcript'
        ID_CARD = 'id_card', 'ID Card'
        CONTRACT = 'contract', 'Contract'
        MEDICAL = 'medical', 'Medical Report'
        ADMISSION_LETTER = 'admission_letter', 'Admission Letter'
        CLEARANCE = 'clearance', 'Clearance Form'
        OTHER = 'other', 'Other'

    class OwnerType(models.TextChoices):
        STUDENT = 'student', 'Student'
        STAFF = 'staff', 'Staff'

    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=30, choices=DocumentType.choices, default=DocumentType.OTHER)
    owner_type = models.CharField(max_length=10, choices=OwnerType.choices)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, null=True, blank=True, related_name='documents')
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='documents')
    file = models.FileField(upload_to='documents/%Y/%m/')
    description = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_documents')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()})"
