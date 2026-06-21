from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.finance_dashboard, name='dashboard'),
    path('students/', views.finance_students, name='students'),
    path('students/<int:student_id>/payments/', views.student_payment_history, name='student_payment_history'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.create_invoice, name='create_invoice'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/generate/', views.generate_invoices, name='generate_invoices'),
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/record/<int:invoice_id>/', views.record_payment, name='record_payment'),
    path('my-fees/', views.my_fees, name='my_fees'),
    path('fee-structure/', views.fee_structure_list, name='fee_structure'),
    path('fee-structure/create/', views.fee_structure_create, name='fee_structure_create'),
    path('fee-structure/<int:pk>/edit/', views.fee_structure_edit, name='fee_structure_edit'),
    path('fee-structure/<int:pk>/delete/', views.fee_structure_delete, name='fee_structure_delete'),
    path('fee-structure/<int:pk>/', views.fee_structure_detail, name='fee_structure_detail'),
    path('scholarships/', views.scholarship_list, name='scholarship_list'),
]
