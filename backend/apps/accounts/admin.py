from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'role', 'status', 'created_at']
    list_filter = ['role', 'status']
    search_fields = ['email', 'name']
    ordering = ['-created_at']
