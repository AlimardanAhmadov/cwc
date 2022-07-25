from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('search-coaches/', views.search_coaches, name='search_coaches')
]