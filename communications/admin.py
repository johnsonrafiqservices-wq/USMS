from django.contrib import admin
from accounts.admin import BaseAdmin
from .models import Announcement, Message, Notification, SMSLog


@admin.register(Announcement)
class AnnouncementAdmin(BaseAdmin):
    list_display = ['title', 'author', 'target_audience', 'priority', 'is_published', 'publish_date']
    list_filter = ['target_audience', 'priority', 'is_published']
    search_fields = ['title', 'content']


@admin.register(Message)
class MessageAdmin(BaseAdmin):
    list_display = ['sender', 'recipient', 'subject', 'is_read', 'sent_at']
    list_filter = ['is_read']


@admin.register(Notification)
class NotificationAdmin(BaseAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']


@admin.register(SMSLog)
class SMSLogAdmin(BaseAdmin):
    list_display = ['recipient_phone', 'recipient_name', 'category', 'status', 'sent_at', 'created_at']
    list_filter = ['status', 'category']
    search_fields = ['recipient_phone', 'recipient_name', 'message']
    readonly_fields = ['sent_at', 'created_at']
