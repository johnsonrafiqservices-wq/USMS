from django.urls import path
from . import views

app_name = 'hostel'

urlpatterns = [
    path('', views.hostel_dashboard, name='dashboard'),
    path('<int:pk>/', views.hostel_detail, name='hostel_detail'),
    path('rooms/', views.room_list, name='room_list'),
    path('allocate/', views.allocate_room, name='allocate_room'),
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
]
