import secrets

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, FormView, ListView, UpdateView

from config.settings import EMAIL_HOST_USER
from users.forms import (CustomAuthenticationForm, CustomPasswordResetForm, CustomPasswordSetForm,
                         CustomUserCreationForm, CustomUserProfileForm, UsersListForm)
from users.models import CustomUser


def UserLogoutView(request):
    logout(request)
    return redirect("sending_mail:index")


class UserLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = "login.html"
    success_url = reverse_lazy("sending_mail:index")


def email_verification(request, token):
    user = get_object_or_404(CustomUser, token=token)
    user.is_active = True
    user.groups.add("Users")
    user.save()
    return redirect(reverse("users:login"))


class RegisterView(FormView):
    model = CustomUser
    template_name = "register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("sending_mail:index")

    def form_valid(self, form):
        user = form.save()

        user.is_active = False
        token = secrets.token_hex(16)  # 16 - шкала чисел
        user.token = token
        user.save()

        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}/"
        send_mail(
            subject="Авторизация на сайте",
            message=f"Для завершения регистрации перейдите по ссылке {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )

        return super().form_valid(form)


class UserProfileView(UpdateView):
    model = CustomUser
    template_name = "profile.html"
    form_class = CustomUserProfileForm
    success_url = reverse_lazy("sending_mail:index")

    def get_object(self):
        return self.request.user


class UserPasswordResetView(FormView):
    template_name = "password_reset.html"
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy("sending_mail:index")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        user = get_object_or_404(CustomUser, email=email)

        token = secrets.token_hex(16)  # 16 - шкала чисел
        user.token = token
        user.save()

        host = self.request.get_host()
        url = f"http://{host}/users/password_reset/{token}/"
        send_mail(
            subject="Восстановление пароля на сайте",
            message=f"Для завершения восстановления пароля перейдите по ссылке {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )

        messages.success(self.request, "Письмо для восстановления пароля было отправлено на ваш электронный адрес.")

        return super().form_valid(form)


def password_confirm(request, token):
    user = get_object_or_404(CustomUser, token=token)

    if request.method == "POST":
        form = CustomPasswordSetForm(user, request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("users:login"))
    else:
        form = CustomPasswordSetForm(user)

    template_name = "password_reset_confirm.html"
    return render(request, template_name, {"form": form})


class UsersListView(LoginRequiredMixin, ListView):
    template_name = "users_list.html"
    form_class = UsersListForm
    context_object_name = "objects_list"
    success_url = reverse_lazy("sending_mail:index")

    def get_queryset(self):
        queryset = CustomUser.objects.all()
        user = self.request.user

        if user.groups.filter(name="Moderator").exists():
            return queryset.exclude(pk=user.pk)

        raise PermissionDenied("У вас недостаточно прав")
        return queryset.none()


class UserDetailView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = "user_detail.html"
    context_object_name = "user_detail"
    form_class = UsersListForm
    success_url = reverse_lazy("users:users_list")


def user_diactive(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    user.is_active = False
    user.save()
    return redirect(reverse("users:user_detail", args=[pk]))


def user_active(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    user.is_active = True
    user.save()
    return redirect(reverse("users:user_detail", args=[pk]))
