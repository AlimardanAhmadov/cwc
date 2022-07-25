import json, re
from django.http import HttpResponse
from django.db import transaction
from coach.models import Coach

from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from reviews.models import Review

from .serializers import ReviewSerializer



class MyHTMLRenderer(TemplateHTMLRenderer):
    def get_template_context(self, *args, **kwargs):
        context = super().get_template_context(*args, **kwargs)
        if isinstance(context, list):
            context = {"items": context}
        return context


class AddReviewView(APIView):
    renderer_classes = [MyHTMLRenderer,]
    template_name = "review/review_form.html"
    permission_classes = (permissions.IsAuthenticated,)
    allowed_methods = ("POST", "GET")
    serialier_class = ReviewSerializer


    def get_serializer(self, *args, **kwargs):
        return ReviewSerializer(*args, **kwargs)
    
    def get(self, request, username):
        profile = self.request.user.profile.cached_by_user(username)
        coach = Coach.cached_by_username(username)
        serializer = ReviewSerializer(profile, coach, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, username):
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            try:
                if hasattr(self.request.user, 'profile'):
                    if serializer.is_valid():
                        review_description = request.data.get('review_description')
                        review_rating = request.data.get('rating')
                        review_summary = request.data.get('review_summary')

                        Review.objects.create(
                            review_description=review_description, 
                            rating=review_rating, 
                            review_summary=review_summary,
                            coach = Coach.cached_by_username(username),
                            reviewer=self.request.user.profile,
                        )
                    
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        data = []
                        emessage=serializer.errors 
                        print(emessage)
                        for key in emessage:
                            err_message = str(emessage[key])
                            print(err_message)
                            err_string = re.search("string='(.*)', code", err_message) 
                            message_value = err_string.group(1)
                            final_message = f"{key} - {message_value}"
                            data.append(final_message)

                        response = HttpResponse(json.dumps({'err': data}), 
                            content_type='application/json')
                        response.status_code = 400
                        return response
                else: 
                    transaction.set_rollback(True)
                    response = HttpResponse(json.dumps({'err': ["You can't add a review as a coach"]}), 
                        content_type='application/json')
                    response.status_code = 400
                    return response
            except Exception as exc: 
                transaction.set_rollback(True)
                response = HttpResponse(json.dumps({'err': ["Something went wrong"]}), 
                    content_type='application/json')
                response.status_code = 400
                return response
