from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="email")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]
    EMAIL_FIELD = "email"

    last_name = models.CharField(
        max_length=150,
        verbose_name="Фамилия",
        help_text="Укажите фамилию",
    )

    first_name = models.CharField(
        max_length=150,
        verbose_name="Имя",
        help_text="Укажите имя",
    )

    middle_name = models.CharField(
        max_length=150,
        verbose_name="Отчество",
        help_text="Укажите отчество",
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Номер телефона",
    )

    token = models.CharField(
        max_length=150,
        verbose_name="Токен",
    )

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
