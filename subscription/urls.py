from django import views
from django.urls import path
from . import views

urlpatterns = [
    path('purchase-subscription', views.PurchaseSubscriptionView.as_view(), name='purchase_subs'),
    path('payment/execute', views.execute, name='execute'),
    path('cancel-subscription', views.CancelUserSubscriptionView.as_view(), name='cancel_subs'),
]