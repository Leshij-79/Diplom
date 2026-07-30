from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "last_name",
        "first_name",
        "middle_name",
        "username",
        "email",
        "is_staff",
        "is_active",
        "date_joined",
        "is_superuser",
        "token",
        "phone_number",
    )

    search_fields = (
        "last_name",
        "username",
        "email",
        "phone_number",
    )

    list_filter = (
        "email",
    )

