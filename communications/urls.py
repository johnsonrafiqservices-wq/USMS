from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    path('announcements/', views.announcements, name='announcements'),
    path('announcements/create/', views.create_announcement, name='create_announcement'),
    path('inbox/', views.inbox, name='inbox'),
    path('sent/', views.sent_messages, name='sent'),
    path('compose/', views.compose_message, name='compose'),
    path('message/<int:pk>/', views.read_message, name='read_message'),
    path('notifications/', views.notifications_view, name='notifications'),
]
