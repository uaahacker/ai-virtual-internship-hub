"""
Root URL configuration.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/assessments/', include('apps.assessments.urls')),
    path('api/tasks/', include('apps.tasks.urls')),
    path('api/chatbot/', include('apps.chatbot.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
]
