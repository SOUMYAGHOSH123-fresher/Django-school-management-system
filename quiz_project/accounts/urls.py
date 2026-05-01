from django.urls import path
from accounts import views
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register-user/', views.RegisterAPIView.as_view(), name='register_user'),
    path('login-user/', views.LoginAPIView.as_view(), name='login_user'),
    path('refresh-token/', TokenRefreshView.as_view(), name='refresh_token'),
    path('log_out/', views.LogoutView, name='logout'),
    
    path('password-reset/', views.RequestPasswordResetAPIView.as_view(), name='password_reset'),
    path('password-reset/done/', views.PasswordRequestSentDoneView, name='password_reset_done'),
    path('reset-password/<uidb64>/<token>/', views.ResetPasswordAPIView.as_view(), name='password_reset_confirm'),
    path("dashboard/profile/", views.UserProfileAPI.as_view(), name='user_profile'),
]