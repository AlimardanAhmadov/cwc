from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('subscriptions/', include('subscriptions.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('', include('user.urls')),
    path('', include('coach.urls')),
    path('', include('main.urls')),
    path('', include('reviews.urls')),
    path('', include('subscription.urls')),

    #path('__debug__/', include('debug_toolbar.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)