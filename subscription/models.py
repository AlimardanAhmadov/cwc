from django.db import models
from django.dispatch import receiver
from django.core.cache import cache
from django.utils.text import slugify
from django.db.models.signals import post_save, post_delete
from subscriptions.models import SubscriptionPlan

from datetime import datetime, timedelta

CACHED_SUBSCRIPTION_BY_ID_KEY = 'subs__by_pk__{}'
CACHED_SUBSCRIPTION_LENGTH = 24 * 3600  # 24hrs

class NotFound:
    """ caching """

class CustomSubscriptionPlan(models.Model):
    selected_subscription_model = models.OneToOneField(SubscriptionPlan, related_name='selected_sub', on_delete=models.CASCADE, blank=True, null=True)
    active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    slug_field = models.SlugField(unique=True, blank=True)
    
    def __str__(self):
        return self.selected_subscription_model.plan_name
    
    @staticmethod
    def cached_by_pk(pk):
        key = CACHED_SUBSCRIPTION_BY_ID_KEY.format(pk)

        coach = cache.get(key)
        if coach:
            if isinstance(coach, NotFound):
                return None
            return coach

        coach = CustomSubscriptionPlan.objects.filter(pk=pk).first()
        
        if not coach:
            cache.set(key, NotFound(), CACHED_SUBSCRIPTION_LENGTH)
            return None

        cache.set(key, coach, CACHED_SUBSCRIPTION_LENGTH)
        return coach

@receiver((post_delete, post_save), sender=CustomSubscriptionPlan)
def invalidate_coach_cache(sender, instance, **kwargs):
    """
    Invalidate the profile cached data when a profile is changed or deleted
    """
    cache.delete(CACHED_SUBSCRIPTION_BY_ID_KEY.format(instance.user.username))

@receiver(post_save, sender=SubscriptionPlan)
def get_next_billing(sender, instance, *args, **kwargs):
    created = kwargs.get('created')
    if created:
        try:
            instance.date_billing_next = datetime.today() + timedelta(days=30)
            instance.date_billing_next = datetime.today() + timedelta(days=30)
            instance.save()
            CustomSubscriptionPlan.objects.create(
                selected_subscription_model=instance,
                slug_field=slugify(instance.plan_name)
            )
        except Exception as exc:
            print(exc)
