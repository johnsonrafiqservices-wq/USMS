from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

app_name = 'academics_api'

router = DefaultRouter()
router.register(r'departments', api_views.DepartmentViewSet)
router.register(r'courses', api_views.CourseViewSet)
router.register(r'sessions', api_views.AcademicSessionViewSet)
router.register(r'semesters', api_views.StudySemesterViewSet)
router.register(r'calendar-events', api_views.AcademicCalendarEventViewSet)
router.register(r'exam-types', api_views.ExamTypeViewSet)
router.register(r'exam-scores', api_views.ExamScoreViewSet)
router.register(r'results', api_views.StudentResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
