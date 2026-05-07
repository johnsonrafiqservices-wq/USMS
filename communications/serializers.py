from rest_framework import serializers
from .models import Announcement, Message, Notification, SMSLog


class AnnouncementSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'author', 'author_name',
                  'target_audience', 'priority', 'is_published',
                  'publish_date', 'expiry_date']


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_name', 'recipient', 'recipient_name',
                  'subject', 'body', 'is_read', 'read_at', 'sent_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'message', 'notification_type',
                  'link', 'is_read', 'created_at']


class SMSLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSLog
        fields = ['id', 'recipient_phone', 'recipient_name', 'user', 'message',
                  'category', 'status', 'provider_reference', 'sent_at', 'created_at']
        read_only_fields = ['sent_at', 'created_at']
