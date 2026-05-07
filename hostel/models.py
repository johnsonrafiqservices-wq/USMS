from django.db import models
from django.conf import settings


class Hostel(models.Model):
    """Hostel/Hall of Residence."""

    class HostelType(models.TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'
        MIXED = 'mixed', 'Mixed'

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    hostel_type = models.CharField(max_length=10, choices=HostelType.choices)
    total_rooms = models.IntegerField(default=0)
    total_capacity = models.IntegerField(default=0)
    address = models.TextField(blank=True)
    warden = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='hostel_warden'
    )
    amenities = models.TextField(blank=True, help_text="Comma-separated list of amenities")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def occupied_beds(self):
        return RoomAllocation.objects.filter(
            room__hostel=self, is_active=True
        ).count()

    @property
    def occupancy_rate(self):
        if self.total_capacity == 0:
            return 0
        return round((self.occupied_beds / self.total_capacity) * 100, 1)


class Room(models.Model):
    """Individual rooms within a hostel."""

    class RoomType(models.TextChoices):
        SINGLE = 'single', 'Single'
        DOUBLE = 'double', 'Double'
        TRIPLE = 'triple', 'Triple'
        QUAD = 'quad', 'Quad (4-person)'

    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20)
    floor = models.IntegerField(default=0)
    room_type = models.CharField(max_length=10, choices=RoomType.choices, default=RoomType.DOUBLE)
    capacity = models.IntegerField(default=2)
    current_occupancy = models.IntegerField(default=0)
    price_per_semester = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    has_bathroom = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    condition = models.CharField(
        max_length=20,
        choices=[('good', 'Good'), ('fair', 'Fair'), ('needs_repair', 'Needs Repair')],
        default='good'
    )

    class Meta:
        unique_together = ['hostel', 'room_number']
        ordering = ['hostel', 'room_number']

    def __str__(self):
        return f"{self.hostel.code} - Room {self.room_number}"

    @property
    def is_full(self):
        return self.current_occupancy >= self.capacity


class RoomAllocation(models.Model):
    """Student room allocation records."""
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='room_allocations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='allocations')
    session = models.ForeignKey('academics.AcademicSession', on_delete=models.CASCADE)
    allocation_date = models.DateField(auto_now_add=True)
    check_in_date = models.DateField(null=True, blank=True)
    check_out_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    allocated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ['student', 'session']
        ordering = ['-allocation_date']

    def __str__(self):
        return f"{self.student} - {self.room}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.is_active:
            self.room.current_occupancy += 1
            self.room.save()

    def deallocate(self):
        self.is_active = False
        self.save()
        self.room.current_occupancy = max(0, self.room.current_occupancy - 1)
        self.room.save()


class MaintenanceRequest(models.Model):
    """Hostel maintenance requests."""

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        URGENT = 'urgent', 'Urgent'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='maintenance_requests')
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    issue = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    resolved_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.room} - {self.issue} ({self.status})"
