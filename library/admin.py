from django.contrib import admin
from accounts.admin import BaseAdmin
from .models import BookCategory, Book, Borrowing, LibraryFine


@admin.register(BookCategory)
class BookCategoryAdmin(BaseAdmin):
    list_display = ['name']


@admin.register(Book)
class BookAdmin(BaseAdmin):
    list_display = ['title', 'author', 'isbn', 'category', 'total_copies', 'available_copies']
    list_filter = ['category', 'is_available']
    search_fields = ['title', 'author', 'isbn']


@admin.register(Borrowing)
class BorrowingAdmin(BaseAdmin):
    list_display = ['book', 'borrower', 'borrow_date', 'due_date', 'status']
    list_filter = ['status']
    search_fields = ['book__title', 'borrower__username']


@admin.register(LibraryFine)
class LibraryFineAdmin(BaseAdmin):
    list_display = ['user', 'amount', 'reason', 'status', 'created_at']
    list_filter = ['status']
