from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('create/', views.student_create, name='student_create'),
    path('<int:pk>/', views.student_detail, name='student_detail'),
    path('<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('my-results/', views.my_results, name='my_results'),
    path('register-courses/', views.course_registration, name='course_registration'),
    path('admissions/', views.admission_list, name='admission_list'),
    path('admissions/<int:pk>/review/', views.admission_review, name='admission_review'),
]
