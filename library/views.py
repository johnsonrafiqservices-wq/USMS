from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from accounts.decorators import role_required
from .models import Book, BookCategory, Borrowing, LibraryFine


@login_required
def catalog(request):
    books = Book.objects.select_related('category').all()
    search = request.GET.get('search')
    category_filter = request.GET.get('category')
    if search:
        books = books.filter(
            Q(title__icontains=search) |
            Q(author__icontains=search) |
            Q(isbn__icontains=search)
        )
    if category_filter:
        books = books.filter(category_id=category_filter)
    categories = BookCategory.objects.all()
    return render(request, 'library/catalog.html', {
        'books': books,
        'categories': categories,
    })


@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    borrowings = Borrowing.objects.filter(book=book).order_by('-borrow_date')[:10]
    return render(request, 'library/book_detail.html', {
        'book': book,
        'borrowings': borrowings,
    })


@login_required
@role_required(['admin', 'librarian'])
def book_list(request):
    books = Book.objects.select_related('category').all()
    search = request.GET.get('search')
    category_filter = request.GET.get('category')
    if search:
        books = books.filter(
            Q(title__icontains=search) |
            Q(author__icontains=search) |
            Q(isbn__icontains=search)
        )
    if category_filter:
        books = books.filter(category_id=category_filter)
    categories = BookCategory.objects.all()
    return render(request, 'library/book_list.html', {
        'books': books,
        'categories': categories,
    })


@login_required
@role_required(['admin', 'librarian'])
def borrowing_list(request):
    borrowings = Borrowing.objects.select_related('book', 'borrower').all()
    status_filter = request.GET.get('status')
    if status_filter:
        borrowings = borrowings.filter(status=status_filter)
    return render(request, 'library/borrowing_list.html', {
        'borrowings': borrowings,
        'statuses': Borrowing.Status.choices,
    })


@login_required
@role_required(['admin', 'librarian'])
def issue_book(request):
    from django.http import JsonResponse
    if request.method == 'POST':
        from accounts.models import User
        book_id = request.POST.get('book')
        user_id = request.POST.get('borrower')
        due_date = request.POST.get('due_date')
        book = get_object_or_404(Book, pk=book_id)
        borrower = get_object_or_404(User, pk=user_id)

        if book.available_copies <= 0:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'No copies available.'})
            messages.error(request, 'No copies available.')
            return redirect('library:catalog')

        Borrowing.objects.create(
            book=book,
            borrower=borrower,
            due_date=due_date,
            issued_by=request.user,
        )
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Book issued to {borrower.get_full_name()}.',
                'redirect': '/library/borrowings/'
            })
        messages.success(request, f'Book issued to {borrower.get_full_name()}.')
        return redirect('library:borrowing_list')

    books = Book.objects.filter(available_copies__gt=0)
    from accounts.models import User
    users = User.objects.filter(is_active=True)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'library/issue_book_fragment.html', {'books': books, 'users': users})

    return render(request, 'library/issue_book.html', {'books': books, 'users': users})


@login_required
@role_required(['admin', 'librarian'])
def return_book(request, borrowing_id):
    borrowing = get_object_or_404(Borrowing, pk=borrowing_id)
    borrowing.return_book()
    if borrowing.is_overdue:
        from django.utils import timezone
        days_overdue = (timezone.now().date() - borrowing.due_date).days
        fine_amount = days_overdue * 50  # 50 per day fine
        LibraryFine.objects.create(
            borrowing=borrowing,
            user=borrowing.borrower,
            amount=fine_amount,
            reason=f'Overdue by {days_overdue} days'
        )
        messages.warning(request, f'Book returned. Fine of {fine_amount} applied for {days_overdue} days overdue.')
    else:
        messages.success(request, 'Book returned successfully.')
    return redirect('library:borrowing_list')


@login_required
def my_books(request):
    """Student's borrowed books."""
    borrowings = Borrowing.objects.filter(borrower=request.user).select_related('book')
    fines = LibraryFine.objects.filter(user=request.user, status='pending')
    return render(request, 'library/my_books.html', {
        'borrowings': borrowings,
        'fines': fines,
    })


@login_required
@role_required(['admin', 'librarian'])
def fine_list(request):
    fines = LibraryFine.objects.select_related('user', 'borrowing__book').all()
    return render(request, 'library/fine_list.html', {'fines': fines})
