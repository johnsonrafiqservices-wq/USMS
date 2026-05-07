from rest_framework.routers import DefaultRouter
from .api_views import StaffProfileViewSet, PayrollViewSet, LeaveRequestViewSet, DocumentViewSet

router = DefaultRouter()
router.register('profiles', StaffProfileViewSet, basename='staff-profile')
router.register('payroll', PayrollViewSet, basename='payroll')
router.register('leave-requests', LeaveRequestViewSet, basename='leave-request')
router.register('documents', DocumentViewSet, basename='document')

urlpatterns = router.urls
