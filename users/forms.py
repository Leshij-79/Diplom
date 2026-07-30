from django.contrib.auth.forms import (AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm,
                                       UserCreationForm)
from django.forms import ModelForm, forms, BooleanField

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


class CustomPasswordResetForm(StyleFormMixin, PasswordResetForm):
    class Meta:
        model = CustomUser
        fields = ("email",)


class CustomPasswordSetForm(StyleFormMixin, SetPasswordForm):
    class Meta:
        model = CustomUser
        fields = (
            "password1",
            "password2",
        )


class CustomPasswordChangeForm(StyleFormMixin, PasswordChangeForm):
    pass


class CustomUserCreationForm(StyleFormMixin, UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
        )

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")

        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError("Номер телефона должен содержать только цифры.")

        return phone_number


class CustomUserProfileForm(StyleFormMixin, ModelForm):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "first_name",
            "last_name",
            "phone_number",
        )


class UsersListForm(StyleFormMixin, ModelForm):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
        )
