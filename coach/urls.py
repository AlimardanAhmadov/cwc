from django.urls import path
from . import views


urlpatterns = [
    path('become-coach/', views.RegisterCoachAPIView.as_view(), name='coachsignup'),
    path('edit-profile/', views.UpdatePesonalInfoView.as_view(), name='edit_profile'), 
    path('add-service/', views.AddServiceView.as_view(), name='add_service'),
    path('update-service/<str:pk>', views.UpdateServiceView.as_view(), name='update_service'),
    path('delete-service/<str:pk>', views.DeleteServiceView.as_view(), name='delete_service'),
    path('change-password', views.ChangePasswordView.as_view(), name="change_password")
]