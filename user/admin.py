from django.contrib import admin

# Register your models here.
from .models import Profile, SMSVerification

admin.site.register(Profile)
admin.site.register(SMSVerification)