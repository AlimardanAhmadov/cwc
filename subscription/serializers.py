from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from subscriptions.models import UserSubscription



class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = ('subscription',)