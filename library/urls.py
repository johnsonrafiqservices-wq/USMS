from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.catalog, name='catalog'),
    path('books/', views.book_list, name='book_list'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('borrowings/', views.borrowing_list, name='borrowing_list'),
    path('issue/', views.issue_book, name='issue_book'),
    path('return/<int:borrowing_id>/', views.return_book, name='return_book'),
    path('my-books/', views.my_books, name='my_books'),
    path('fines/', views.fine_list, name='fine_list'),
]
