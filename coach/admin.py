from django.contrib import admin
from .models import Coach, Service


# admin.site.register(Coach)
admin.site.register(Service)


class ServiceInline(admin.StackedInline):
    model = Service
    extra = 0
    fields = ['service_title', 'service_description']

class CoachAdmin(admin.ModelAdmin):
    inlines = [ServiceInline]

admin.site.register(Coach, CoachAdmin)