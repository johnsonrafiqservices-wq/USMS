from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class BookCategory(models.Model):
    """Book categories/genres."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Book Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    """Library book catalog."""
    title = models.CharField(max_length=300)
    isbn = models.CharField(max_length=20, unique=True, verbose_name='ISBN')
    author = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200, blank=True)
    publication_year = models.IntegerField(null=True, blank=True)
    edition = models.CharField(max_length=50, blank=True)
    category = models.ForeignKey(BookCategory, on_delete=models.SET_NULL, null=True, related_name='books')
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    shelf_location = models.CharField(max_length=50, blank=True)
    cover_image = models.ImageField(upload_to='library/covers/', null=True, blank=True)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    added_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} by {self.author}"

    @property
    def is_borrowed_out(self):
        return self.available_copies <= 0


class Borrowing(models.Model):
    """Book borrowing records."""

    class Status(models.TextChoices):
        BORROWED = 'borrowed', 'Borrowed'
        RETURNED = 'returned', 'Returned'
        OVERDUE = 'overdue', 'Overdue'
        LOST = 'lost', 'Lost'

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrowings')
    borrower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='borrowings')
    borrow_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateField()
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.BORROWED)
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='issued_books'
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-borrow_date']

    def __str__(self):
        return f"{self.book.title} - {self.borrower.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = (timezone.now() + timedelta(days=14)).date()
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.status == self.Status.BORROWED:
            self.book.available_copies -= 1
            self.book.save()

    def return_book(self):
        self.return_date = timezone.now()
        self.status = self.Status.RETURNED
        self.save()
        self.book.available_copies += 1
        self.book.save()

    @property
    def is_overdue(self):
        if self.status == self.Status.BORROWED:
            return timezone.now().date() > self.due_date
        return False


class LibraryFine(models.Model):
    """Fines for overdue or lost books."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        WAIVED = 'waived', 'Waived'

    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE, related_name='fines')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='library_fines')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    paid_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.amount} ({self.status})"
