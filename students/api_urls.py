from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

app_name = 'students_api'

router = DefaultRouter()
router.register(r'students', api_views.StudentViewSet)
router.register(r'year-enrollments', api_views.AcademicYearEnrollmentViewSet)
router.register(r'enrollments', api_views.EnrollmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
