from django.contrib import admin
from subscriptions.models import PlanCost, UserSubscription, SubscriptionTransaction, PlanListDetail, SubscriptionPlan


class SubscriptionInline(admin.StackedInline):
    model = PlanCost
    extra = 0
    
class SubscriptionAdmin(admin.ModelAdmin):
    inlines = [SubscriptionInline]


admin.site.register(SubscriptionPlan, SubscriptionAdmin)
admin.site.register(UserSubscription)
admin.site.register(SubscriptionTransaction)
admin.site.register(PlanListDetail)