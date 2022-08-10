import base64, random, string
from datetime import datetime, timezone, timedelta
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.core.files.base import ContentFile
from django.dispatch import receiver
from django.conf import settings
from django.core.cache import cache
from phonenumber_field.modelfields import PhoneNumberField 
from user.models import SMSVerification
from model_utils import FieldTracker

User = get_user_model()

CACHED_COACH_BY_ID_KEY = 'coach__by_user__{}'
CACHED_SERVICE_BY_ID_KEY = 'service__by_pk__{}'
CACHED_COACH_QUERYSET = 'cached__coach_queryset__{}'
CACHED_SERVICE_QUERYSET = 'cached__service_queryset__{}'
CACHED_COACH_LENGTH = 24 * 3600  # 24hrs


class NotFound:
    """ caching """


def id_generator(size=30, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/users/<username>/<filename>
    return "users/{0}/{1}".format(instance.user.username, filename)


def national_image_path(instance, filename):
    return f"national/{instance.user.username}/images/{filename}"


class TimeStampedModel(models.Model):
    created = models.DateTimeField(db_index=True, auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Coach(TimeStampedModel):
    user = models.OneToOneField(User, related_name="coach", on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to=user_directory_path, default='default.png')
    phone_number = PhoneNumberField(blank=True)
    about = models.TextField(blank=True, null=True)
    available_days = models.CharField(max_length=400, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    timing = models.CharField(max_length=200, null=True, blank=True)
    full_name = models.CharField(max_length=250, null=True, blank=True)
    location = models.CharField(max_length=250, blank=True, null=True)
    rating = models.DecimalField(max_digits = 5,decimal_places = 1, blank=True, default=0.0)
    image_url = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    paid = models.BooleanField(default=False)

    tracker = FieldTracker()

    class Meta:
        verbose_name = 'Coach'
        verbose_name_plural = 'Coaches'
        indexes = [models.Index(fields=['user', 'id', 'paid', 'category', 'full_name', 'location'])]

    def __str__(self):
        return "%s" % self.user.username

    @staticmethod
    def cached_by_username(username):
        key = CACHED_COACH_BY_ID_KEY.format(username)

        coach = cache.get(key)
        if coach:
            if isinstance(coach, NotFound):
                return None
            return coach

        coach = Coach.objects.filter(user__username=username).first()

        if not coach:
            cache.set(key, NotFound(), CACHED_COACH_LENGTH)
            return None

        cache.set(key, coach, CACHED_COACH_LENGTH)
        return coach

    @staticmethod
    def cached_queryset():
        key = CACHED_SERVICE_QUERYSET.format(id_generator())

        coaches = cache.get(key)
        if coaches:
            if isinstance(coaches, NotFound):
                return None
            return coaches

        coaches = Coach.objects.filter(paid=True)

        if not coaches:
            cache.set(key, NotFound(), CACHED_COACH_LENGTH)
            return None

        cache.set(key, coaches, CACHED_COACH_LENGTH)
        return coaches

    def save(self, *args, **kwargs):
        new_url = self.tracker.has_changed('image_url')
        if new_url and ';base64,' in self.image_url:
            format, imgstr = self.image_url.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            self.profile_picture = data
        super(Coach, self).save(*args, **kwargs)

    @property
    def last_seen(self):
        return cache.get(f"seen_{self.user.username}")

    @property
    def online(self):
        if self.last_seen:
            now = datetime.now(timezone.utc)
            if now > self.last_seen + timedelta(minutes=settings.USER_ONLINE_TIMEOUT):
                return False
            else:
                return True
        else:
            return False

@receiver((post_delete, post_save), sender=Coach)
def invalidate_coach_cache(sender, instance, **kwargs):
    """
    Invalidate the coach cached data when a coach is changed or deleted
    """
    cache.delete(CACHED_COACH_BY_ID_KEY.format(instance.user.username))

@receiver((post_delete, post_save), sender=Coach)
def invalidate_coach_queryset_cache(sender, instance, **kwargs):
    """
    Invalidate the coach cached data when a coach is changed or deleted
    """
    cache.delete(CACHED_COACH_QUERYSET.format(id_generator()))


class Service(models.Model):
    related_coach = models.ForeignKey(Coach, on_delete=models.CASCADE)
    service_title = models.CharField(max_length=550)
    service_description = models.TextField()
    created = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['created']
        indexes = [models.Index(fields=['related_coach',])]

    @staticmethod
    def cached_by_pk(pk):
        key = CACHED_SERVICE_BY_ID_KEY.format(pk)

        coach = cache.get(key)
        if coach:
            if isinstance(coach, NotFound):
                return None
            return coach

        coach = Coach.objects.filter(pk=pk).first()

        if not coach:
            cache.set(key, NotFound(), CACHED_COACH_LENGTH)
            return None

        cache.set(key, coach, CACHED_COACH_LENGTH)
        return coach

    @staticmethod
    def cached_queryset(profile):
        key = CACHED_COACH_BY_ID_KEY.format(profile)

        coaches = cache.get(key)
        if coaches:
            if isinstance(coaches, NotFound):
                return None
            return coaches

        services = Service.objects.filter(related_coach=profile)

        if not services:
            cache.set(key, NotFound(), CACHED_COACH_LENGTH)
            return None

        cache.set(key, services, CACHED_COACH_LENGTH)
        return services


    def __str__(self):
        return self.service_title

@receiver((post_delete, post_save), sender=Service)
def invalidate_service_cache(sender, instance, **kwargs):
    """
    Invalidate the service cached data when a service is changed or deleted
    """
    cache.delete(CACHED_SERVICE_BY_ID_KEY.format(instance.pk))


@receiver((post_delete, post_save), sender=Service)
def invalidate_service_queryset_cache(sender, instance, **kwargs):
    """
    Invalidate the service cached data when a service is changed or deleted
    """
    cache.delete(CACHED_SERVICE_QUERYSET.format(instance.related_coach))

"""@receiver(post_save, sender=Coach)
def send_sms_verification(sender, instance, *args, **kwargs):
    created = kwargs.get('created')

    if created:
        try:
            sms = instance.user.sms
            if sms:
                pin = sms.pin
                sms.delete()
                verification = SMSVerification.objects.create(
                    user=instance.user,
                    phone=instance.user.coach.phone_number,
                    sent=True,
                    verified=True,
                    pin=pin,
                )
        except:
            if instance.user.coach.phone_number:
                verification = SMSVerification.objects.create(
                    user=instance.user, phone=instance.user.coach.phone_number
                )
                verification.send_confirmation()"""
