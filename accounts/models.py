from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Custom User model with role-based access control."""

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        REGISTRAR = 'registrar', 'Registrar'
        LECTURER = 'lecturer', 'Lecturer'
        STUDENT = 'student', 'Student'
        FINANCE = 'finance', 'Finance Staff'
        LIBRARIAN = 'librarian', 'Librarian'
        HOSTEL_MANAGER = 'hostel_manager', 'Hostel Manager'
        FACULTY_DEAN = 'faculty_dean', 'Faculty Dean'
        DEPARTMENT_HEAD = 'department_head', 'Department Head'
        PROGRAMME_COORDINATOR = 'programme_coordinator', 'Programme Coordinator'

    role = models.CharField(max_length=25, choices=Role.choices, default=Role.STUDENT)
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
        blank=True
    )
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_active_member = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_registrar(self):
        return self.role == self.Role.REGISTRAR

    @property
    def is_lecturer(self):
        return self.role == self.Role.LECTURER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_finance_staff(self):
        return self.role == self.Role.FINANCE

    @property
    def is_librarian(self):
        return self.role == self.Role.LIBRARIAN

    @property
    def is_faculty_dean(self):
        return self.role == self.Role.FACULTY_DEAN

    @property
    def is_department_head(self):
        return self.role == self.Role.DEPARTMENT_HEAD

    @property
    def is_programme_coordinator(self):
        return self.role == self.Role.PROGRAMME_COORDINATOR


class AuditLog(models.Model):
    """Track all system actions for security and compliance."""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=100, blank=True)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"
