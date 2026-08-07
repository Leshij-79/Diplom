import re

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms import BooleanField, forms

from users.models import CustomUser


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"


class CustomAuthenticationForm(StyleFormMixin, AuthenticationForm):
    class Meta(AuthenticationForm):
        model = CustomUser
        fields = ("username", "password")


class CustomUserCreationForm(StyleFormMixin, UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "last_name",
            "first_name",
            "middle_name",
            "email",
            "phone_number",
        )

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")

        if phone_number:
            phone_number = phone_number.strip()

            cleaned = re.sub(r"[^\d+]", "", phone_number)

            if not re.match(r"^\+?\d+$", cleaned):
                raise forms.ValidationError("Номер телефона должен содержать только цифры и знак '+' в начале.")

            digits_only = re.sub(r"\D", "", cleaned)
            if len(digits_only) < 10:
                raise forms.ValidationError("Номер телефона должен содержать минимум 10 цифр.")

            if len(digits_only) > 15:
                raise forms.ValidationError("Номер телефона не должен содержать более 15 цифр.")

            if cleaned.startswith("8") and len(cleaned) == 11:
                cleaned = "+7" + cleaned[1:]
            elif cleaned.startswith("7") and len(cleaned) == 11:
                cleaned = "+" + cleaned
            elif not cleaned.startswith("+") and len(cleaned) == 10:
                cleaned = "+7" + cleaned
            elif not cleaned.startswith("+") and len(cleaned) == 11:
                cleaned = "+" + cleaned

        return phone_number
