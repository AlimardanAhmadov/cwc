from django.urls import path
from . import views


urlpatterns = [
    path('add_review/<str:username>', views.AddReviewView.as_view(), name='add_review'),
]