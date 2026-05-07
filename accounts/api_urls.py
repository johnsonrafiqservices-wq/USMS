from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import api_views

app_name = 'accounts_api'

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', api_views.UserProfileAPIView.as_view(), name='api_profile'),
    path('users/', api_views.UserListAPIView.as_view(), name='api_user_list'),
]
