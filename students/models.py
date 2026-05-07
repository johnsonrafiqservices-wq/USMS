from django.db import models
from django.db.models import Sum
from django.conf import settings
from django.utils import timezone


class Student(models.Model):
    """Student profile linked to User account."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending Admission'
        ADMITTED = 'admitted', 'Admitted'
        ACTIVE = 'active', 'Active'
        SUSPENDED = 'suspended', 'Suspended'
        GRADUATED = 'graduated', 'Graduated'
        WITHDRAWN = 'withdrawn', 'Withdrawn'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    programme = models.ForeignKey('academics.Programme', on_delete=models.SET_NULL, null=True, related_name='students')
    current_year = models.ForeignKey('academics.StudyYear', on_delete=models.SET_NULL, null=True, related_name='students')
    current_semester_number = models.ForeignKey('academics.StudySemester', on_delete=models.SET_NULL, null=True, related_name='students')
    intake = models.ForeignKey(
        'academics.Intake', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='students'
    )
    admission_date = models.DateField(default=timezone.now)
    expected_graduation = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    nationality = models.CharField(max_length=100, blank=True)
    state_of_origin = models.CharField(max_length=100, blank=True)
    lga = models.CharField(max_length=100, blank=True, verbose_name='LGA')
    guardian_name = models.CharField(max_length=200, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True)
    guardian_email = models.EmailField(blank=True)
    guardian_relationship = models.CharField(max_length=50, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    medical_conditions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['student_id']

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"

    @property
    def full_name(self):
        return self.user.get_full_name()

    @property
    def level_display(self):
        year = self.current_year.name if self.current_year else '—'
        semester = self.current_semester_number.name if self.current_semester_number else '—'
        return f"{year}, {semester}"

    def calculate_gpa(self, semester=None):
        """Calculate GPA for a specific semester or current."""
        from academics.models import StudentResult
        results = StudentResult.objects.filter(student=self, is_published=True)
        if semester:
            results = results.filter(course_allocation__semester=semester)

        total_points = 0
        total_credits = 0
        for result in results:
            credits = result.course_allocation.course.credit_units
            total_points += float(result.grade_point) * credits
            total_credits += credits

        if total_credits == 0:
            return 0.0
        return round(total_points / total_credits, 2)

    def calculate_cgpa(self):
        """Calculate Cumulative GPA across all semesters."""
        return self.calculate_gpa()

    def check_graduation_eligibility(self):
        """Return dict with eligibility status and reasons."""
        from academics.models import StudentResult
        reasons = []

        if self.status not in ('active', 'admitted'):
            reasons.append(f"Status is '{self.status}', must be active.")

        programme = self.programme
        if not programme:
            return {'eligible': False, 'reasons': ['No programme assigned.']}

        required_credits = programme.total_credits
        earned_credits = sum(
            r.course_allocation.course.credit_units
            for r in StudentResult.objects.filter(
                student=self, is_published=True, grade_point__gte=1.0
            ).select_related('course_allocation__course')
        )
        if earned_credits < required_credits:
            reasons.append(
                f"Insufficient credits: {earned_credits}/{required_credits} earned."
            )

        cgpa = self.calculate_cgpa()
        if cgpa < 1.0:
            reasons.append(f"CGPA {cgpa} below minimum pass threshold of 1.0.")

        unpaid = self._check_outstanding_fees()
        if unpaid:
            reasons.append(f"Outstanding fees balance: {unpaid}.")

        return {'eligible': len(reasons) == 0, 'earned_credits': earned_credits,
                'required_credits': required_credits, 'cgpa': cgpa, 'reasons': reasons}

    def _check_outstanding_fees(self):
        try:
            from finance.models import Invoice
            total = Invoice.objects.filter(
                student=self, status__in=['pending', 'overdue']
            ).aggregate(s=models.Sum('balance'))['s'] or 0
            return float(total)
        except Exception:
            return 0


class AcademicYearEnrollment(models.Model):
    """Tracks a student's enrollment in a specific year and semester of study."""

    class EnrollmentStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'
        REPEATED = 'repeated', 'Repeated'
        DEFERRED = 'deferred', 'Deferred'
        WITHDRAWN = 'withdrawn', 'Withdrawn'

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='year_enrollments')
    academic_session = models.ForeignKey('academics.AcademicSession', on_delete=models.CASCADE, related_name='year_enrollments')
    semester = models.ForeignKey('academics.StudySemester', on_delete=models.SET_NULL, null=True, blank=True, related_name='year_enrollments')
    year_of_study = models.ForeignKey('academics.StudyYear', on_delete=models.PROTECT, related_name='year_enrollments')
    semester_number = models.ForeignKey('academics.StudySemester', on_delete=models.PROTECT, related_name='semester_enrollments')
    status = models.CharField(max_length=20, choices=EnrollmentStatus.choices, default=EnrollmentStatus.ACTIVE)
    enrolled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='enrolled_students'
    )
    enrollment_date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)

    class Meta:
        unique_together = ['student', 'academic_session', 'year_of_study', 'semester_number']
        ordering = ['-academic_session__name', 'year_of_study__level', 'semester_number__number']
        verbose_name = 'Academic Year Enrollment'
        verbose_name_plural = 'Academic Year Enrollments'

    def __str__(self):
        year = self.year_of_study.name if self.year_of_study else '?'
        sem = self.semester_number.name if self.semester_number else '?'
        return f"{self.student.student_id} – {year} {sem} ({self.academic_session})"

    @property
    def label(self):
        year = self.year_of_study.name if self.year_of_study else '?'
        sem = self.semester_number.name if self.semester_number else '?'
        return f"{year}, {sem}"


class Enrollment(models.Model):
    """Student course enrollment per semester."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey('academics.Course', on_delete=models.CASCADE, related_name='enrollments')
    semester = models.ForeignKey('academics.StudySemester', on_delete=models.CASCADE, related_name='enrollments')
    academic_year_enrollment = models.ForeignKey(
        AcademicYearEnrollment, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='course_enrollments'
    )
    enrollment_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_retake = models.BooleanField(default=False, help_text="Mark if this is a retake of a previously failed course")

    class Meta:
        unique_together = ['student', 'course', 'semester']
        ordering = ['-enrollment_date']

    def __str__(self):
        retake_tag = " (Retake)" if self.is_retake else ""
        return f"{self.student.student_id} - {self.course.code} ({self.semester}){retake_tag}"


class AdmissionApplication(models.Model):
    """Admission application tracking."""

    class Status(models.TextChoices):
        SUBMITTED = 'submitted', 'Submitted'
        UNDER_REVIEW = 'under_review', 'Under Review'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'
        WAITLISTED = 'waitlisted', 'Waitlisted'

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    programme_applied = models.ForeignKey('academics.Programme', on_delete=models.SET_NULL, null=True)
    session = models.ForeignKey('academics.AcademicSession', on_delete=models.SET_NULL, null=True)
    intake = models.ForeignKey(
        'academics.Intake', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='applications'
    )
    previous_school = models.CharField(max_length=200, blank=True)
    qualification = models.CharField(max_length=200, blank=True)
    grade = models.CharField(max_length=50, blank=True)
    documents = models.FileField(upload_to='admissions/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    remarks = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    application_date = models.DateTimeField(auto_now_add=True)
    decision_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-application_date']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.programme_applied}"
