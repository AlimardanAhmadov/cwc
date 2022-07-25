from django.urls import path, include
from django.views.generic import TemplateView
from . import views
from rest_auth.views import (
    LogoutView,
)


urlpatterns = [
    path("login/", views.LoginAPIView.as_view(), name="account_login"),
    path(
        "reset/password/", views.PasswordResetView.as_view(), name="rest_password_reset"
    ),
    path(
        "password/change/",
        views.PasswordChangeView.as_view(),
        name="rest_password_change",
    ),
    path("", include("rest_auth.urls")),
    path("sign-up/", views.RegisterAPIView.as_view(), name="signup"),
    path(
        "account-confirm-email/sent/",
        TemplateView.as_view(),
        name="account_confirm_email",
    ),
    path(
        "password/reset/confirm/<str:uidb64>/<str:token>/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("verify-sms/<str:username>", views.VerifySMSView.as_view()),
    path("resend-sms/<str:username>/", views.resend_otp),

    path('users/<str:username>/coach_dashboard', views.UserProfileAPIView.as_view(), name='subs_edit_profile'), 
    path('coach/<str:username>', views.ProfileAPIView.as_view(), name='profile_overview'), 
    path('user-profile', views.MyProfileAPIView.as_view(), name='user_profile'), 
    path('update-profile/', views.UpdateProfileAPIView.as_view(), name='update_profile'),
    path('logout/', views.LogoutView.as_view(), name="logout"),
]
