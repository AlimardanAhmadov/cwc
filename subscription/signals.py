from django.dispatch import receiver
from django.db.models.signals import post_save
from datetime import datetime, timedelta
from subscriptions.models import SubscriptionPlan


@receiver(post_save, sender=SubscriptionPlan)
def get_next_billing(sender, instance, *args, **kwargs):
    created = kwargs.get('created')
    if created:
        try:
            instance.date_billing_next = datetime.today() + timedelta(days=30)
            instance.date_billing_next = datetime.today() + timedelta(days=30)
            instance.save()
        except Exception as exc:
            print(exc)

