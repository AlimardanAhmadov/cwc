import json, re
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db import transaction
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required 
from django.views.decorators.debug import sensitive_post_parameters
from rest_auth.utils import jwt_encode 
from rest_auth.app_settings import JWTSerializer
from rest_framework import permissions, status, generics
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from rest_framework.generics import (
    ListCreateAPIView
)

from .serializers import (ChangePasswordSerializer, CustomCoachRegisterSerializer, ServiceSerializer, UpdateCoachSerializer, CreateUpdateServiceSerializer)
from .models import Coach, Service

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters("password1", "password2")
)

class MyHTMLRenderer(TemplateHTMLRenderer):
    def get_template_context(self, *args, **kwargs):
        context = super().get_template_context(*args, **kwargs)
        if isinstance(context, list):
            context = {"items": context}
        return context



class RegisterCoachAPIView(ListCreateAPIView):
    renderer_classes = [MyHTMLRenderer,]
    template_name = "coach/signup.html"
    queryset = Coach.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = CustomCoachRegisterSerializer
    
    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(RegisterCoachAPIView, self).dispatch(*args, **kwargs)

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = CustomCoachRegisterSerializer(users, many=True)
        return Response(serializer.data)

    def get_serializer(self, *args, **kwargs):
        return CustomCoachRegisterSerializer(*args, **kwargs)

    def get_response_data(self, user):
        data = {"user": user, "token": self.token}
        return JWTSerializer(data).data

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
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
        except Exception:
            response = HttpResponse(json.dumps({'err': "Something went wrong!"}), 
                content_type='application/json')
            response.status_code = 406
            return response

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        if getattr(settings, "REST_USE_JWT", False):
            self.token = jwt_encode(user)
        return user


class UpdatePesonalInfoView(ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    template_name = 'coach/edit_profile_info.html'
    renderer_classes = [MyHTMLRenderer,]
    serializer_class = UpdateCoachSerializer

    
    @method_decorator(login_required(login_url='/#login-modal'))
    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(UpdatePesonalInfoView, self).dispatch(*args, **kwargs)

    def get(self, request, format=None):
        user = self.request.user
        serializer = UpdateCoachSerializer(user, context={'request': request})
        return Response(data=serializer.data)

    def get_serializer(self, *args, **kwargs):
        return UpdateCoachSerializer(*args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            try:
                user = self.request.user
                serializer = UpdateCoachSerializer(user, data=request.data, context={'request': request})
                if serializer.is_valid():
                    user.coach.full_name = request.data.get('full_name')
                    user.email = request.data.get('email')
                    user.coach.phone_number = request.data.get('phone_number')
                    user.coach.category = request.data.get('category')
                    user.coach.available_days = request.data.get('available_days')
                    user.coach.timing = request.data.get('timing')
                    user.coach.image_url = request.data.get('image_url')
                    user.coach.about = request.data.get('about')
                    user.coach.save()
                    return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    transaction.set_rollback(True)
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
                transaction.set_rollback(True)
                response = HttpResponse(json.dumps({'err': {'Something went wrong'}}), 
                    content_type='application/json')
                response.status_code = 400
                return response


class AddServiceView(ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    template_name = 'coach/edit_profile.html'
    renderer_classes = [MyHTMLRenderer,]
    serializer_class = CreateUpdateServiceSerializer

    @method_decorator(login_required(login_url='/#login-modal'))
    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(AddServiceView, self).dispatch(*args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            try:
                user = self.request.user
                serializer = CreateUpdateServiceSerializer(data=request.data, context={'request': request})
                if serializer.is_valid():
                    new_service = Service.objects.create(
                        related_coach = user.coach,
                        service_title = request.data.get('service_title'),
                        service_description = request.data.get('service_description'),
                    )
                    return JsonResponse({'data': serializer.data, 'service_title':str(new_service.service_title), 'service_description':str(new_service.service_description), 'service_id':str(new_service.id)})
            except Exception as exc:
                print(exc)
                transaction.set_rollback(True)
                response = HttpResponse(json.dumps({'err': 'something went wrong'}), 
                content_type='application/json')
                response.status_code = 400
                return response


class UpdateServiceView(ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    template_name = 'coach/edit_profile.html'
    renderer_classes = [MyHTMLRenderer,]
    serializer_class = CreateUpdateServiceSerializer

    @method_decorator(login_required(login_url='/#login-modal'))
    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(UpdateServiceView, self).dispatch(*args, **kwargs)

    def get(self, pk, format=None):
        try:
            service = Service.cached_by_pk(pk)
            if service:
                "Cache calling"
            else:
                service = get_object_or_404(Service, id=pk)

            return service
        except Service.DoesNotExist:
            response = HttpResponse(json.dumps({'err': 'something went wrong'}), 
                content_type='application/json')
            response.status_code = 404
            return response


    @transaction.atomic
    def create(self, request, pk):
        with transaction.atomic():
            try:
                service = self.get(pk)

                serializer = CreateUpdateServiceSerializer(service, data=request.data, context={'request': request})
                if serializer.is_valid():
                    service.service_title = request.data.get('service_title')
                    service.service_description = request.data.get('service_description')
                    service.save()
                return JsonResponse(serializer.data, status=status.HTTP_200_OK)
            except Service.DoesNotExist:
                transaction.set_rollback(True)
                response = HttpResponse(json.dumps({'err': 'Service is not found'}), 
                    content_type='application/json')
                response.status_code = 404
                return response
            except Exception as exc:
                print(exc)
                transaction.set_rollback(True)
                response = HttpResponse(json.dumps({'err': 'Something went wrong'}), 
                    content_type='application/json')
                response.status_code = 400
                return response


class DeleteServiceView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    template_name = 'coach/edit_profile.html'
    renderer_classes = [MyHTMLRenderer,]
    serializer_class = ServiceSerializer
    allowed_methods = ("OPTIONS", "GET", "DELETE")


    @method_decorator(login_required(login_url='/#login-modal'))
    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(DeleteServiceView, self).dispatch(*args, **kwargs)

    def get_object(self, pk):
        try:
            service = get_object_or_404(Service, id=pk)
            return service
        except Service.DoesNotExist:
            response = HttpResponse(json.dumps({'err': 'Something went wrong'}), 
                content_type='application/json')
            response.status_code = 404
            return response

    def get(self, request, pk, format=None):
        service = self.get_object(pk)
        serializer = ServiceSerializer(service, context={'request': request})
        return Response(serializer.data)


    def post(self, request, pk, format=None):
        service = self.get_object(pk) 
        service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    template_name = 'coach/edit_profile.html'
    renderer_classes = [MyHTMLRenderer,]
    serializer_class = ChangePasswordSerializer

    @method_decorator(login_required(login_url='/#login-modal'))
    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(ChangePasswordView, self).dispatch(*args, **kwargs)
    
    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(ChangePasswordView, self).dispatch(*args, **kwargs)

    def get(self, request, format=None):
        user = self.request.user
        serializer = ChangePasswordSerializer(user, context={'request': request})
        return Response(data=serializer.data)

    def get_serializer(self, *args, **kwargs):
        return ChangePasswordSerializer(*args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            try:
                user = self.request.user
                serializer = ChangePasswordSerializer(user, data=request.data, context={'request': request})
                if serializer.is_valid():
                    user.set_password(request.data.get("password"))
                    user.save()
                    return JsonResponse(serializer.data, status=status.HTTP_200_OK)
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
                response = HttpResponse(json.dumps({'err': data}), 
                    content_type='application/json')
                response.status_code = 400
                return response
