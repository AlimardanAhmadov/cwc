import logging, base64
from datetime import datetime, timezone, timedelta
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.core.files.base import ContentFile
from django.dispatch import receiver
from django.conf import settings
from django.core.cache import cache
from rest_framework.exceptions import NotAcceptable
from phonenumber_field.modelfields import PhoneNumberField
from randompinfield import RandomPinField
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from model_utils import FieldTracker


User = get_user_model()

CACHED_PROFILE_BY_ID_KEY = 'profile__by_user__{}'
CACHED_PROFILE_LENGTH = 24 * 3600  # 24hrs


class NotFound:
    """ caching """


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


class Profile(TimeStampedModel):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to=user_directory_path, blank=True)
    image_url = models.TextField(blank=True, null=True)
    phone_number = PhoneNumberField(blank=True)
    about = models.TextField(blank=True, null=True)
    full_name = models.CharField(max_length=250, blank=True, null=True)
    paid = models.BooleanField(default=False)
    tracker = FieldTracker()

    class Meta:
        indexes = [models.Index(fields=['user', 'id', 'paid',])]

    def __str__(self):
        return "%s" % self.user.username

    @staticmethod
    def cached_by_username(username):
        key = CACHED_PROFILE_BY_ID_KEY.format(username)

        profile = cache.get(key)
        if profile:
            if isinstance(profile, NotFound):
                return None
            return profile

        profile = Profile.objects.filter(user__username=username).first()

        if not profile:
            cache.set(key, NotFound(), CACHED_PROFILE_LENGTH)
            return None

        cache.set(key, profile, CACHED_PROFILE_LENGTH)
        return profile
    

    def save(self, *args, **kwargs):
        new_url = self.tracker.has_changed('image_url')
        if new_url and ';base64,' in self.image_url:
            format, imgstr = self.image_url.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            self.profile_picture = data
        super(Profile, self).save(*args, **kwargs)

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

@receiver((post_delete, post_save), sender=Profile)
def invalidate_coach_cache(sender, instance, **kwargs):
    """
    Invalidate the profile cached data when a profile is changed or deleted
    """
    cache.delete(CACHED_PROFILE_BY_ID_KEY.format(instance.user.username))


class SMSVerification(TimeStampedModel):
    user = models.OneToOneField(User, related_name="sms", on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)
    pin = RandomPinField(length=6)
    sent = models.BooleanField(default=False)
    phone = PhoneNumberField(null=False, blank=False)

    def send_confirmation(self):

        logging.debug("Sending PIN %s to phone %s" % (self.pin, self.phone))

        if all(
            [
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN,
                settings.TWILIO_FROM_NUMBER,
            ]
        ):
            try:
                twilio_client = Client(
                    settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN
                )
                twilio_client.messages.create(
                    body="Your CWC verification code is: %s." % self.pin,
                    to=str(self.phone),
                    from_=settings.TWILIO_FROM_NUMBER,
                )
                self.sent = True
                self.save()
                return True
            except TwilioRestException as e:
                logging.error(e)
        else:
            logging.warning("Twilio credentials are not set")

    def confirm(self, pin):
        if pin == self.pin:
            self.verified = True
            self.save()
        else:
            raise NotAcceptable("your Pin is wrong, or this phone is verified before.")

        return self.verified


@receiver(post_save, sender=Profile)
def send_sms_verification(sender, instance, *args, **kwargs):
    if instance.created:
        try:
            sms = instance.user.sms
            if sms:
                pin = sms.pin
                sms.delete()
                verification = SMSVerification.objects.create(
                    user=instance.user,
                    phone=instance.user.profile.phone_number,
                    sent=True,
                    verified=True,
                    pin=pin,
                )
        except:
            if instance.user.profile.phone_number:
                verification = SMSVerification.objects.create(
                    user=instance.user, phone=instance.user.profile.phone_number
                )
                verification.send_confirmation()
