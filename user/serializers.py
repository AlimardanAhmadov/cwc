from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from django.core.validators import EmailValidator
from django.contrib.auth.models import User
from rest_framework import serializers, exceptions
from phonenumber_field.serializerfields import PhoneNumberField
from rest_auth.registration.serializers import RegisterSerializer
from rest_framework.validators import UniqueValidator 
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.utils.translation import gettext_lazy as _
from allauth.account.models import EmailAddress
from .models import Profile, SMSVerification

# Get the UserModel
UserModel = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(style={"input_type": "password"})

    def authenticate(self, **kwargs):
        return authenticate(self.context["request"], **kwargs)

    def _validate_email(self, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            msg = _('Must include "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username(self, username, password):
        user = None

        if username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _(
                'Must include "username or "email" or "phone number" and "password".'
            )
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username_email(self, username, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        elif username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _(
                'Must include either "username" or "email" or "phone number" and "password".'
            )
            raise exceptions.ValidationError(msg)

        return user

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = None

        if username:
            user = self._validate_username_email(username, "", password)

        if user:
            if not user.is_active:
                msg = _("User account is inactive.")
                raise exceptions.ValidationError(msg)
        else:
            msg = _("please check your username or password.")
            raise exceptions.ValidationError(msg)

        if "rest_auth.registration" in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            if (
                app_settings.EMAIL_VERIFICATION
                == app_settings.EmailVerificationMethod.MANDATORY
            ):
                try:
                    email_address = user.emailaddress_set.get(email=user.email)
                except EmailAddress.DoesNotExist:
                    raise serializers.ValidationError(
                        _(
                            "This account don't have E-mail address!, so that you can't login."
                        )
                    )
                if not email_address.verified:
                    raise serializers.ValidationError(_("E-mail is not verified."))
 
        try:
            phone_number = user.sms
        except SMSVerification.DoesNotExist:
            raise serializers.ValidationError(
                _("This account don't have Phone Number!")
            )
        if not phone_number.verified:
            raise serializers.ValidationError(_("The phone number is not verified."))

        attrs["user"] = user
        return attrs


class CustomRegisterSerializer(RegisterSerializer):
    username = serializers.CharField(required=True, write_only=True)
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    email = serializers.EmailField(required=True, write_only=True)
    phone_number = PhoneNumberField(
        required=True,
        write_only=True,
        validators=[
            UniqueValidator(
                queryset=Profile.objects.all(),
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
            "profile_picture": self.validated_data.get("profile_picture", ""),
            "image_url": self.validated_data.get("image_url", ""),
        }

    def create_profile(self, user, validated_data):
        user.first_name = self.validated_data.get("first_name")
        user.last_name = self.validated_data.get("last_name")
        user.save()

        Profile.objects.create(
            user=user,
            phone_number = self.validated_data.get("phone_number"),
            full_name = self.validated_data.get("first_name") + " " + self.validated_data.get("last_name"),
            image_url = self.validated_data.get('image_url'),
        )

    def custom_signup(self, request, user):
        self.create_profile(user, self.get_cleaned_data_profile())


class SMSVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSVerification
        exclude = ("modified", )


class SMSPinSerializer(serializers.Serializer):
    class Meta:
        model = SMSVerification
        fields = ["pin", ]


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = Profile
        fields = ["user", "profile_picture", "phone_number", "full_name", "about"]



class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(source="profile.profile_picture")
    about = serializers.CharField(source="profile.about")
    phone_number = PhoneNumberField(source="profile.phone_number")
    online = serializers.BooleanField(source="profile.online")

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "online",
            "last_login",
            "about",
            "phone_number",
            "profile_picture",
            "is_active",
        ]


class UserMiniSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(source="profile.profile_picture")
    gender = serializers.CharField(source="profile.gender")
    phone_number = PhoneNumberField(source="profile.phone_number")

    class Meta:
        model = get_user_model()
        fields = ["username", "profile_picture", "gender", "phone_number"]


class UpdateUserProfileSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    
    phone_number = PhoneNumberField(source="profile.phone_number")
    full_name = serializers.CharField(source="profile.full_name")
    image_url = serializers.CharField(source="profile.image_url")

    class Meta:
        model = User
        fields = (
            "email",
            "phone_number",
            "full_name",
            "image_url"
            )
        
        extra_kwargs = {
            'email': {'validators': [EmailValidator,]},
        }
    

class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': _('Token is invalid or expired')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')
