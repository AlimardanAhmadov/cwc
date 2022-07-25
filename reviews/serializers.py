from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Review


User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['review_summary', 'review_description', 'rating']

      