from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="email")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]
    EMAIL_FIELD = "email"

    avatar = models.ImageField(upload_to="media/avatars", blank=True, null=True, verbose_name="Аватар")
    phone_number = models.CharField(blank=True, null=True, max_length=15, verbose_name="Номер телефона")
    country = models.CharField(blank=True, null=True, max_length=50, verbose_name="Страна")
    token = models.CharField(max_length=150, verbose_name="Токен")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["email"]
        permissions = [
            ("can_view_user", "Может просматривать пользователей"),
            ("can_block_user", "Может блокировать пользователей"),
        ]

    def __str__(self):
        return self.email
