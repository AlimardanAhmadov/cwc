import json, re
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.shortcuts import get_object_or_404 
from django.db import transaction
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import (
    GenericAPIView,
    ListCreateAPIView,

)
from rest_framework.exceptions import NotAcceptable
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from rest_auth.views import (
    LoginView,
    PasswordResetConfirmView,
    PasswordChangeView,
)
from rest_auth.serializers import PasswordResetConfirmSerializer
from rest_auth.app_settings import JWTSerializer
from rest_auth.utils import jwt_encode 
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from coach.models import Coach, Service
from coach.serializers import CoachSerializer, ServiceSerializer
from reviews.models import Review
from .models import Profile, SMSVerification
from .serializers import (
    ProfileSerializer,
    UserSerializer,
    SMSPinSerializer,
    CustomRegisterSerializer,
    UpdateUserProfileSerializer,
    RefreshTokenSerializer
)
from .send_mail import send_reset_password_email

from django.contrib.auth import get_user_model

from subscriptions.models import UserSubscription



User = get_user_model()

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters("password1", "password2")
)


class MyHTMLRenderer(TemplateHTMLRenderer):
    def get_template_context(self, *args, **kwargs):
        context = super().get_template_context(*args, **kwargs)
        if isinstance(context, list):
            context = {"items": context}
        return context

class LoginAPIView(LoginView):
    queryset = ""
    renderer_classes = [MyHTMLRenderer,]
    template_name = "main/base.html"
    allowed_methods = ("POST", "OPTIONS", "HEAD", "GET")

    def get_response(self):
        serializer_class = self.get_response_serializer()
        if getattr(settings, "REST_USE_JWT", False):
            data = {"user": self.user, "token": self.token}
            serializer = serializer_class(
                instance=data, context={"request": self.request}
            )
        else:
            serializer = serializer_class(
                instance=self.token, context={"request": self.request}
            )
        response = JsonResponse(serializer.data, status=status.HTTP_200_OK)

        return response

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(
            data=self.request.data, context={"request": request}
        )
        if self.serializer.is_valid():
            self.login()
        else:
            data = []
            emessage=self.serializer.errors 
            print(emessage)
            for key in emessage:
                err_message = str(emessage[key])
                print(err_message)
                err_string = re.search("string=(.*), ", err_message) 
                message_value = err_string.group(1)
                final_message = f"{message_value}"
                data.append(final_message)

            response = HttpResponse(json.dumps({'error': data}), 
                content_type='application/json')
            response.status_code = 400
            return response
        return self.get_response()


class RegisterAPIView(ListCreateAPIView):
    renderer_classes = [MyHTMLRenderer,]
    template_name = "user/signup.html"
    queryset = Profile.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = CustomRegisterSerializer
    
    
    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(RegisterAPIView, self).dispatch(*args, **kwargs)

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = CustomRegisterSerializer(users, many=True)
        return Response(serializer.data)

    def get_serializer(self, *args, **kwargs):
        return CustomRegisterSerializer(*args, **kwargs)

    def get_response_data(self, user):
        data = {"user": user, "token": self.token}
        return JWTSerializer(data).data

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = self.perform_create(serializer)
            if getattr(settings, "REST_USE_JWT", False):
                self.token = jwt_encode(user)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        else:
            data = []
            emessage=serializer.errors 
            print(emessage)
            for key in emessage:
                err_message = str(emessage[key])
                print(err_message)
                err_string = re.search("string=(.*), ", err_message) 
                message_value = err_string.group(1)
                final_message = f"{key} - {message_value}"
                data.append(final_message)

            response = HttpResponse(json.dumps({'error': data}), 
                content_type='application/json')
            response.status_code = 400
            return response

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        if getattr(settings, "REST_USE_JWT", False):
            self.token = jwt_encode(user)

        email = EmailAddress.objects.get(email=user.email, user=user)
        confirmation = EmailConfirmationHMAC(email)
        key = confirmation.key
        print("account-confirm-email/" + key)
        return user


@api_view(["POST"])
def resend_otp(request, username):
    with transaction.atomic():
        try:
            sms = get_object_or_404(SMSVerification, user__username=username)

            phone = sms.phone
            sms_verification = sms

            user = User.objects.filter(profile__phone_number=phone).first()

            if sms_verification is None:
                sms_verification = SMSVerification.objects.create(user=user, phone=phone)
            
            success = sms_verification.send_confirmation()

            return Response(dict(success=success), status=status.HTTP_200_OK)
        except Exception as exc:
            print(exc)
            transaction.set_rollback(True)
            response = HttpResponse(json.dumps({'err': "Something went wrong!"}), 
                content_type='application/json')
            response.status_code = 406
            return response


class VerifySMSView(APIView):
    renderer_classes = [MyHTMLRenderer,]
    template_name = "user/verify_otp.html"
    permission_classes = (permissions.AllowAny,)
    allowed_methods = ("POST", "OPTIONS", "HEAD", "GET")
    serialier_class = SMSPinSerializer

    def get_serializer(self, *args, **kwargs):
        return SMSPinSerializer(*args, **kwargs)
    
    def get(self, request, username):
        serializer = SMSPinSerializer(context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, username):
        serializer = self.get_serializer(data=request.data)
        with transaction.atomic():
            try:
                if serializer.is_valid():
                    pin = int(request.data.get("pin"))
                    confirmation = get_object_or_404(SMSVerification, user__username=username)
                    confirmation.confirm(pin=pin)
                    return JsonResponse({'data':serializer.data, 'status':status.HTTP_200_OK})
                else:
                    data = []
                    emessage=serializer.errors 
                    print(emessage)
                    for key in emessage:
                        err_message = str(emessage[key])
                        err_string = re.search("string='(.*)', ", err_message) 
                        message_value = err_string.group(1)
                        final_message = f"{key} - {message_value}"
                        data.append(final_message)
                    response = HttpResponse(json.dumps({'err': data}), 
                        content_type='application/json')
                    response.status_code = 400
                    return response
            except Exception:
                transaction.set_rollback(True)
                response = HttpResponse(json.dumps({'err': "Code is not acceptable"}),
                    content_type='application/json')
                response.status_code = 406
                return response


class PasswordResetView(APIView):
    def post(self, request, *args, **kwargs):

        email = request.data.get("email", None)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise NotAcceptable(_("Please enter a valid email."))
        send_reset_password_email.delay(user)
        return Response(
            {"detail": _("Password reset e-mail has been sent.")},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = PasswordResetConfirmSerializer

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(PasswordResetConfirmView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("Password has been reset with the new password.")})


class UserProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    template_name = 'coach/edit_profile.html'
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, username):
        profile = Coach.cached_by_username(username)
        related_services = Service.cached_queryset(profile)
        service_serializer = ServiceSerializer(related_services, many=True, context={"request": request})
        profile_serializer = CoachSerializer(profile, context={"request": request})
        reviews = Review.objects.filter(coach=profile).order_by('-created')
        context = {'data': profile_serializer.data,'reviews': reviews, 'username': username, 'services': service_serializer.data, 'status':status.HTTP_200_OK}
        if self.request.user.coach.paid == True:
            next_due_payment = UserSubscription.objects.get(user=self.request.user)
            context['next_due_payment'] = next_due_payment.date_billing_next
        return Response(context)


class ProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    template_name = 'user/profile_overview.html'
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, username):
        profile = Coach.cached_by_username(username)
        related_services = Service.cached_queryset(profile)
        service_serializer = ServiceSerializer(related_services, many=True, context={"request": request})
        profile_serializer = CoachSerializer(profile, context={"request": request})
        reviews = Review.objects.filter(coach=profile).order_by('-created')
        context = {'data': profile_serializer.data, 'reviews': reviews, 'username': username, 'services': service_serializer.data, 'status':status.HTTP_200_OK}
        return Response(context)


class MyProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    template_name = 'user/profile.html'
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request):
        user = self.request.user
        profile = user.profile.cached_by_username(user.username)
        if profile:
            print("Calling cache")
        else:
            profile = user.profile
        serializer = ProfileSerializer(profile, context={"request": request})
        user_serializer = UserSerializer(user, context={'request': request})
        context = {'data': serializer.data, 'user': user_serializer.data, 'status':status.HTTP_200_OK}
        if profile.paid:
            next_due_payment = get_object_or_404(UserSubscription, user=user)
            context['next_due_payment'] = next_due_payment.date_billing_next
        return Response(context)


class UpdateProfileAPIView(ListCreateAPIView):
    renderer_classes = [MyHTMLRenderer,]
    template_name = "user/profile.html"
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UpdateUserProfileSerializer
    
    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(UpdateProfileAPIView, self).dispatch(*args, **kwargs)

    def get(self, request, format=None):
        users = self.request.user
        serializer = UpdateUserProfileSerializer(users, context={'request': request})
        return Response(serializer.data)

    def get_serializer(self, *args, **kwargs):
        return UpdateUserProfileSerializer(*args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            try:
                user = self.request.user
                serializer = UpdateUserProfileSerializer(user, data=request.data, context={'request': request})
                if serializer.is_valid():
                    user.profile.image_url = request.data.get('image_url')
                    user.profile.full_name = request.data.get('full_name')
                    user.email = request.data.get('email')
                    user.profile.phone_number = request.data.get('phone_number')
                    user.profile.save()
                    return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    data = []
                    emessage=serializer.errors 
                    print(emessage)
                    for key in emessage:
                        err_message = str(emessage[key])
                        err_string = re.search("string='(.*)', ", err_message) 
                        message_value = err_string.group(1)
                        final_message = f"{key} - {message_value}"
                        data.append(final_message)

                    response = HttpResponse(json.dumps({'err': data}), 
                        content_type='application/json')
                    response.status_code = 400
                    return response
            except Exception as exc:
                print(exc)
                transaction.set_rollback(True)
                response = HttpResponse(json.dumps({'err': {'Something went wrong'}}), 
                        content_type='application/json')
                response.status_code = 400
                return response


class LogoutView(ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    allowed_methods = ('GET', 'POST')
    serializer_class = RefreshTokenSerializer
    

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

