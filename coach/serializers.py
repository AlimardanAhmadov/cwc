from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm
from django.core.validators import EmailValidator
from django.contrib.auth.password_validation import validate_password
from django.forms import CharField
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from rest_auth.registration.serializers import RegisterSerializer
from rest_framework.validators import UniqueValidator
from drf_extra_fields.fields import Base64ImageField
from user.models import SMSVerification
from .models import Coach, Service

# Get the UserModel
UserModel = get_user_model()


class CoachSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    profile_picture = Base64ImageField()


    class Meta:
        model = Coach
        fields = '__all__'


class CustomCoachRegisterSerializer(RegisterSerializer):
    username = serializers.CharField(required=True, write_only=True)
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    email = serializers.EmailField(required=True, write_only=True)
    category = serializers.CharField(required=True, write_only=True)
    about = serializers.CharField(required=True, write_only=True)
    available_days = serializers.CharField(required=True, write_only=True)
    timing = serializers.CharField(required=True, write_only=True)
    phone_number = PhoneNumberField(
        required=True,
        write_only=True,
        validators=[
            UniqueValidator(
                queryset=Coach.objects.all(),
                message=_("A user is already registered with this phone number."),
            )
        ],
    )
    image_url = serializers.CharField(required=True, write_only=True)

    def get_cleaned_data_profile(self):
        return {
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
            "phone_number": self.validated_data.get("phone_number", ""),
            "category": self.validated_data.get("category", ""),
            "available_days": self.validated_data.get("available_days", ""),
            "about": self.validated_data.get("about", ""),
            "timing": self.validated_data.get("timing", ""),
            "profile_picture": self.validated_data.get("profile_picture", ""),
            "image_url": self.validated_data.get("image_url", ""),
        }

    def create_profile(self, user, validated_data):
        user.first_name = self.validated_data.get("first_name")
        user.last_name = self.validated_data.get("last_name")
        user.save()
        
        Coach.objects.create(
            user=user,
            phone_number = self.validated_data.get("phone_number"),
            category = self.validated_data.get("category"),
            available_days = self.validated_data.get("available_days"),
            about = self.validated_data.get("about"),
            timing = self.validated_data.get("timing"),
            image_url = self.validated_data.get('image_url'),
            full_name = self.validated_data.get('first_name') + ' ' + self.validated_data.get('last_name')
        )

    def custom_signup(self, request, user):
        self.create_profile(user, self.get_cleaned_data_profile())


class ServiceSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Service
        fields = ('pk', 'service_title', 'service_description')


class CreateUpdateServiceSerializer(serializers.Serializer):
    service_title = serializers.CharField(required=True, write_only=True)
    service_description = serializers.CharField(required=True, write_only=True)
    

class SMSVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSVerification
        exclude = ("modified", )


class SMSPinSerializer(serializers.Serializer):
    class Meta:
        model = SMSVerification
        fields = ["pin", ]


class UpdateCoachSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    
    phone_number = PhoneNumberField(source="coach.phone_number")
    category = serializers.CharField(source="coach.category")
    available_days = serializers.CharField(source="coach.available_days")
    timing = serializers.CharField(source="coach.timing")
    image_url = serializers.CharField(source="coach.image_url")
    full_name = serializers.CharField(source="coach.full_name")

    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "phone_number",
            "full_name",
            'category',
            'available_days',
            'timing',
            'image_url'
        )
        
        extra_kwargs = {
            'email': {'validators': [EmailValidator,]},
        }


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'old_password',
            'password', 
            'password2',
            )

    set_password_form_class = SetPasswordForm

    def __init__(self, *args, **kwargs):
        self.old_password_field_enabled = getattr(
            settings, "OLD_PASSWORD_FIELD_ENABLED", False
        )
        self.logout_on_password_change = getattr(
            settings, "LOGOUT_ON_PASSWORD_CHANGE", False
        )
        super(ChangePasswordSerializer, self).__init__(*args, **kwargs)

        self.request = self.context.get("request")
        self.user = getattr(self.request, "user", None)

    def validate_old_password(self, value): 
        invalid_password_conditions = (
            self.user,
            not self.user.check_password(value),
        )

        if all(invalid_password_conditions):
            raise serializers.ValidationError("Invalid password")
        return value

    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": 'Password fields did not match.'})
      
        
        old_password_match = (
            attrs["old_password"] == attrs["password"],
        )

        if all(old_password_match):
            raise serializers.ValidationError(
                {"password": 'your new password matching with old password'}
            )
        
        return attrs

    