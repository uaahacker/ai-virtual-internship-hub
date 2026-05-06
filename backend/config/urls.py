"""
Root URL configuration.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/assessments/', include('apps.assessments.urls')),
    path('api/tasks/', include('apps.tasks.urls')),
    path('api/chatbot/', include('apps.chatbot.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/portfolios/', include('apps.portfolios.urls')),
    path('api/submissions/', include('apps.submissions.urls')),
]

# Serve media files in development (nginx handles this in production)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
