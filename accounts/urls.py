from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('users/', views.user_list_view, name='user_list'),
    path('users/register/', views.register_user_view, name='register_user'),
    path('quick-create/<str:action>/', views.quick_create_view, name='quick_create'),
    path('db-management/', views.db_management_view, name='db_management'),
    path('api/db/export/', views.export_database_api, name='export_db'),
    path('api/db/import/', views.import_database_api, name='import_db'),
]
