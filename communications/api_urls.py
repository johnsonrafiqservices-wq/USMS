from rest_framework.routers import DefaultRouter
from .api_views import AnnouncementViewSet, MessageViewSet, NotificationViewSet, SMSLogViewSet

router = DefaultRouter()
router.register('announcements', AnnouncementViewSet, basename='announcement')
router.register('messages', MessageViewSet, basename='message')
router.register('notifications', NotificationViewSet, basename='notification')
router.register('sms-logs', SMSLogViewSet, basename='sms-log')

urlpatterns = router.urls
