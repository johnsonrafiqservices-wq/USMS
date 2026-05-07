from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class StudyLevel(models.Model):
    """Academic study level (e.g., Certificate, Diploma, Bachelor's, Master's, PhD)."""
    name = models.CharField(max_length=50, unique=True, help_text="e.g. Certificate, Diploma, Bachelor's Degree")
    code = models.CharField(max_length=20, unique=True, help_text="e.g. CERT, DIP, BSC, MSC, PHD")
    level_number = models.IntegerField(unique=True, help_text="e.g. 1 for Certificate, 2 for Diploma, 3 for Bachelor's, etc.")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['level_number']
        verbose_name = 'Study Level'
        verbose_name_plural = 'Study Levels'

    def __str__(self):
        return f"{self.code} - {self.name}"


class StudyYear(models.Model):
    """Academic year of study (e.g., Year 1, Year 2, etc.)."""
    code = models.CharField(max_length=10, unique=True, help_text="e.g. Y1, Y2, Y3")
    name = models.CharField(max_length=50, help_text="e.g. Year 1, Year 2")
    level = models.IntegerField(unique=True, help_text="e.g. 1 for Year 1, 2 for Year 2")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['level']

    def __str__(self):
        return f"{self.code} — {self.name}"


class StudySemester(models.Model):
    """Semester number within a year (e.g., Semester 1, Semester 2)."""
    code = models.CharField(max_length=10, unique=True, help_text="e.g. S1, S2")
    name = models.CharField(max_length=50, help_text="e.g. Semester 1, Semester 2")
    number = models.IntegerField(unique=True, help_text="e.g. 1 for Semester 1, 2 for Semester 2")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"{self.code} — {self.name}"


class Campus(models.Model):
    """University Campus location."""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)
    location = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Faculty(models.Model):
    """University Faculty/College."""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name='faculties', null=True, blank=True)
    dean = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='faculty_dean'
    )
    description = models.TextField(blank=True)
    established_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Faculties'
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Department(models.Model):
    """Academic Department within a Faculty."""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')
    head_of_department = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='department_head'
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Programme(models.Model):
    """Academic Programme (e.g., BSc Computer Science)."""
    class Schedule(models.TextChoices):
        FULLTIME = 'fulltime', 'Full-time'
        WEEKEND = 'weekend', 'Weekend'
        EVENING = 'evening', 'Evening'
        ONLINE = 'online', 'Online'
        HOLIDAY = 'holiday', 'Holiday'

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programmes')
    level = models.ForeignKey(StudyLevel, on_delete=models.PROTECT, related_name='programmes')
    schedule = models.CharField(max_length=10, choices=Schedule.choices, default=Schedule.FULLTIME)
    duration_years = models.IntegerField(default=4)
    total_credits = models.IntegerField(default=120)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class AcademicSession(models.Model):
    """Academic Year (e.g. 2026/2027) — standalone, no dates."""
    name = models.CharField(max_length=50, unique=True)  # e.g., "2026/2027"
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicSession.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)


class Intake(models.Model):
    """Student intake cohort — standalone, identified by code and name."""

    code = models.CharField(max_length=20, unique=True, help_text="e.g. AUG2026, JAN2027")
    name = models.CharField(max_length=100, help_text="e.g. August 2026 Intake")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Intake'
        verbose_name_plural = 'Intakes'

    def __str__(self):
        return f"{self.code} — {self.name}"

    @property
    def student_count(self):
        return self.students.count()


class Course(models.Model):
    """Course/Module offered by a department."""
    class CourseType(models.TextChoices):
        CORE = 'core', 'Core'
        ELECTIVE = 'elective', 'Elective'
        GENERAL = 'general', 'General Education'

    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    programme = models.ManyToManyField(Programme, related_name='courses', blank=True)
    credit_units = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(6)])
    course_type = models.CharField(max_length=10, choices=CourseType.choices, default=CourseType.CORE)
    level = models.IntegerField(default=100, help_text="Course level (100, 200, 300, etc.)")
    semester = models.ForeignKey(StudySemester, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    description = models.TextField(blank=True)
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='is_prerequisite_for')
    max_students = models.IntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.title}"


class CourseAllocation(models.Model):
    """Allocation of courses to lecturers per semester."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='allocations')
    lecturer = models.ForeignKey(
        'staff.StaffProfile', on_delete=models.CASCADE, related_name='course_allocations'
    )
    semester = models.ForeignKey(StudySemester, on_delete=models.CASCADE, related_name='allocations')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['course', 'lecturer', 'semester']

    def __str__(self):
        return f"{self.course.code} - {self.lecturer} ({self.semester})"


class Timetable(models.Model):
    """Class scheduling/timetable."""
    class Day(models.TextChoices):
        MONDAY = 'mon', 'Monday'
        TUESDAY = 'tue', 'Tuesday'
        WEDNESDAY = 'wed', 'Wednesday'
        THURSDAY = 'thu', 'Thursday'
        FRIDAY = 'fri', 'Friday'
        SATURDAY = 'sat', 'Saturday'

    course_allocation = models.ForeignKey(CourseAllocation, on_delete=models.CASCADE, related_name='timetable_slots')
    day = models.CharField(max_length=3, choices=Day.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50)
    building = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['day', 'start_time']

    def __str__(self):
        return f"{self.course_allocation.course.code} - {self.get_day_display()} {self.start_time}-{self.end_time}"


class Attendance(models.Model):
    """Student attendance tracking."""
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='attendances')
    course_allocation = models.ForeignKey(CourseAllocation, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    remarks = models.CharField(max_length=200, blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'course_allocation', 'date']
        ordering = ['-date']

    def __str__(self):
        status = "Present" if self.is_present else "Absent"
        return f"{self.student} - {self.course_allocation.course.code} - {self.date} ({status})"


class GradeScale(models.Model):
    """Grading scale configuration."""
    grade = models.CharField(max_length=5)  # A, B+, B, C+, etc.
    min_score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2)
    description = models.CharField(max_length=50, blank=True)  # Excellent, Good, etc.

    class Meta:
        ordering = ['-min_score']

    def __str__(self):
        return f"{self.grade} ({self.min_score}-{self.max_score}) = {self.grade_point}"


class AcademicCalendarEvent(models.Model):
    """Academic calendar events (deadlines, holidays, exam periods)."""
    class EventType(models.TextChoices):
        HOLIDAY = 'holiday', 'Public Holiday'
        EXAM_PERIOD = 'exam_period', 'Exam Period'
        REGISTRATION = 'registration', 'Registration Deadline'
        COURSE_ADD = 'course_add', 'Course Add Deadline'
        COURSE_DROP = 'course_drop', 'Course Drop Deadline'
        GRADUATION = 'graduation', 'Graduation'
        ORIENTATION = 'orientation', 'Orientation'
        OTHER = 'other', 'Other'

    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EventType.choices, default=EventType.OTHER)
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='calendar_events', null=True, blank=True)
    semester = models.ForeignKey(StudySemester, on_delete=models.CASCADE, related_name='calendar_events', null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return f"{self.title} ({self.start_date})"


class ExamType(models.Model):
    """Types of assessments (CAT, Midterm, Final, Coursework, Resit)."""
    class Category(models.TextChoices):
        CONTINUOUS = 'continuous', 'Continuous Assessment'
        MIDTERM = 'midterm', 'Midterm'
        FINAL = 'final', 'Final Exam'
        COURSEWORK = 'coursework', 'Coursework'
        RESIT = 'resit', 'Resit / Supplementary'
        PRACTICAL = 'practical', 'Practical'

    name = models.CharField(max_length=50)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.CONTINUOUS)
    weight = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage weight (e.g. 30 for 30%)")
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.weight}%)"


class ExamScore(models.Model):
    """Individual score for a specific exam type for a student in a course."""
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='exam_scores')
    course_allocation = models.ForeignKey(CourseAllocation, on_delete=models.CASCADE, related_name='exam_scores')
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE, related_name='scores')
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    remarks = models.CharField(max_length=200, blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='recorded_scores')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'course_allocation', 'exam_type']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.student_id} - {self.course_allocation.course.code} - {self.exam_type.name}: {self.score}"


class StudentResult(models.Model):
    """Aggregated student result for a course, with approval workflow."""

    class ApprovalStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        SUBMITTED = 'submitted', 'Submitted by Lecturer'
        HOD_APPROVED = 'hod_approved', 'Approved by HOD'
        REGISTRAR_APPROVED = 'registrar_approved', 'Approved by Registrar'
        PUBLISHED = 'published', 'Published'
        REJECTED = 'rejected', 'Rejected'

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='results')
    course_allocation = models.ForeignKey(CourseAllocation, on_delete=models.CASCADE, related_name='results')
    ca_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Continuous Assessment")
    exam_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grade = models.CharField(max_length=5, blank=True)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    is_resit = models.BooleanField(default=False, help_text="Is this a resit/supplementary result?")
    approval_status = models.CharField(max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.DRAFT)
    is_published = models.BooleanField(default=False)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='recorded_results')
    approved_by_hod = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='hod_approved_results')
    approved_by_registrar = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='registrar_approved_results')
    hod_approved_at = models.DateTimeField(null=True, blank=True)
    registrar_approved_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'course_allocation']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student} - {self.course_allocation.course.code}: {self.grade}"

    def calculate_grade(self):
        """Calculate grade from total score using grade scale."""
        self.total_score = self.ca_score + self.exam_score
        try:
            scale = GradeScale.objects.get(
                min_score__lte=self.total_score,
                max_score__gte=self.total_score
            )
            self.grade = scale.grade
            self.grade_point = scale.grade_point
        except GradeScale.DoesNotExist:
            self.grade = 'F'
            self.grade_point = 0
        self.save()
