from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.conf import settings
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from rest_framework.generics import (
    ListCreateAPIView
)
import json, re, paypalrestsdk

from .serializers import SubscriptionSerializer
from subscriptions.models import UserSubscription, PlanCost, SubscriptionPlan

from .tasks import create_payment_model, recurring_payment_warning
from .refund import refund_customer



paypalrestsdk.configure({
    "mode": "sandbox", # sandbox or live
    "client_id": settings.PAYPAL_CLIENT_ID,
    'client_secret': settings.PAYPAL_CLIENT_SECRET}
)

class MyHTMLRenderer(TemplateHTMLRenderer):
    def get_template_context(self, *args, **kwargs):
        context = super().get_template_context(*args, **kwargs)
        if isinstance(context, list):
            context = {"items": context}
        return context

def get_subscription_price():
    active_subscription = SubscriptionPlan.objects.filter()[:1].get()
    plan_cost = PlanCost.objects.filter(plan=active_subscription)[:1].get()
    return plan_cost.cost
    

class PurchaseSubscriptionView(ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    template_name = 'subscription/checkout.html'
    renderer_classes = [MyHTMLRenderer,]
    serializer_class = SubscriptionSerializer

    def get(self, request, format=None):
        selected_subscription = SubscriptionPlan.objects.filter()[:1].get()
        serializer = SubscriptionSerializer(selected_subscription, data=request.data, context={'request': request})
        return Response(serializer.data)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            try:
                active_subscription = SubscriptionPlan.objects.filter()[:1].get()
                serializer = SubscriptionSerializer(active_subscription, data=request.data, context={'request': request})
                
                if serializer.is_valid():
                    cost = int(get_subscription_price().normalize())
                    plan_cost = float("{0:.2f}".format(cost))

                    billing_plan = paypalrestsdk.Payment({
                        "intent": "sale",
                        "payer": {
                            "payment_method": "paypal"},
                        "redirect_urls": {
                            "return_url": "http://127.0.0.1:8000/payment/execute",
                            "cancel_url": "http://127.0.0.1:8000/"},
                        "transactions": [{
                            "item_list": {
                                "items": [{
                                    "name": "CWC Subscription Plan",
                                    "sku": "cwc-subscription-plan",
                                    "price": str(plan_cost),
                                    "currency": "USD",
                                    "quantity": 1}]},
                            "amount": {
                                "total": str(plan_cost),
                                "currency": "USD"},
                            "description": "This is a payment transaction description."}]})
                    response = billing_plan.create()

                    if response:
                        print("Payment created successfully")

                        for link in billing_plan.links:
                            if link.rel == "approval_url":
                                approval_url = str(link.href)
                                self.request.session["payment_id"] = billing_plan.id
                                return JsonResponse({'redirect_value': approval_url})
                                # return HttpResponseRedirect(approval_url)
                    else:
                        transaction.set_rollback(True)
                        print(billing_plan.error)
                        
                else:
                    transaction.set_rollback(True)
                    data = []
                    emessage=serializer.errors 
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
                response = HttpResponse(json.dumps({'err': "Something went wrong"}),
                        content_type='application/json')
                response.status_code = 400
                return response
            

def execute(request):
    with transaction.atomic():
        payment_id = request.session.get("payment_id")
        payment = paypalrestsdk.Payment.find(payment_id)

        if payment.execute({'payer_id':request.GET.get("PayerID")}):
            current_user = request.user
            active_subscription = SubscriptionPlan.objects.filter()[:1].get()
            active_plan_cost = PlanCost.objects.filter(plan=active_subscription)[:1].get()

            if UserSubscription.objects.filter(subscription=active_plan_cost).exists():
                user_subs = get_object_or_404(UserSubscription, subscription=active_plan_cost)
            else:
                user_subs = UserSubscription.objects.create(
                    subscription=active_plan_cost,
                    user = current_user,
                    date_billing_start=timezone.now(),
                    date_billing_last=timezone.now(),
                    date_billing_next=timezone.now() + timedelta(days=31)
                )
            
            create_payment_model.delay(current_user.id, payment_id)

            next_month = datetime.utcnow() + timedelta(days=31)
            recurring_payment_warning.apply_async(args=[current_user.id, ], eta=next_month)

            if user_subs:
                if hasattr(request.user, 'profile'):
                    request.user.profile.paid = True
                    request.user.profile.save()

                elif hasattr(request.user, 'coach'):
                    request.user.coach.paid = True
                    request.user.coach.save()
                else:
                    print("Nothing is happening")
        else:
            print(payment.error)
            transaction.set_rollback(True)
        if hasattr(request.user, 'coach'):
            redirect_url = "/users/{}/coach_dashboard".format(request.user.username)
        else:
            redirect_url = "/user-profile"
        return redirect(redirect_url)



class CancelUserSubscriptionView(ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    template_name = 'coach/edit_profile.html'
    renderer_classes = [MyHTMLRenderer,]
    serializer_class = SubscriptionSerializer

    def get(self, request, format=None):
        current_user = self.request.user
        user_subs = get_object_or_404(UserSubscription, user__username=current_user.username)
        serializer = SubscriptionSerializer(user_subs, context={'request': request})
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        with transaction.atomic():
            current_user = self.request.user
            try:
                user_subs = get_object_or_404(UserSubscription, user__username=current_user.username)
                serializer = SubscriptionSerializer(user_subs, context={'request': request})
                if user_subs.delete():
                    #refund_customer.delay(current_user.payment.order_id, user_subs.subscription.cost)

                    if hasattr(current_user, 'profile'):
                        current_user.profile.paid = False
                        current_user.profile.save()

                    elif hasattr(current_user, 'coach'):
                        current_user.coach.paid = False
                        current_user.coach.save()
                    else:
                        transaction.set_rollback(True)
                        print("Nothing is happening")
                    return JsonResponse(serializer.data, status=status.HTTP_200_OK)
            except Exception as exc:
                print(exc)
                transaction.set_rollback(True)
                return Response(status=status.HTTP_404_NOT_FOUND)

