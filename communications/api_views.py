from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Announcement, Message, Notification, SMSLog
from .serializers import AnnouncementSerializer, MessageSerializer, NotificationSerializer, SMSLogSerializer


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.select_related('author').all()
    serializer_class = AnnouncementSerializer
    filterset_fields = ['target_audience', 'priority', 'is_published']
    search_fields = ['title', 'content']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    filterset_fields = ['is_read']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Message.objects.none()
        user = self.request.user
        return Message.objects.filter(
            recipient=user
        ).select_related('sender', 'recipient')

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        msg = self.get_object()
        msg.is_read = True
        msg.read_at = timezone.now()
        msg.save()
        return Response({'status': 'read'})


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    filterset_fields = ['is_read', 'notification_type']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({'status': 'all marked read'})


class SMSLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SMSLog.objects.all()
    serializer_class = SMSLogSerializer
    filterset_fields = ['status', 'category']
    permission_classes = [permissions.IsAdminUser]
