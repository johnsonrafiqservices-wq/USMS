from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard, name='dashboard'),
    path('financial/', views.financial_report, name='financial'),
    path('academic/', views.academic_report, name='academic'),
    path('attendance/', views.attendance_report, name='attendance'),
    path('export/students/', views.export_students_excel, name='export_students'),
]
