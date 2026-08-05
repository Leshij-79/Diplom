import secrets

from django.contrib.auth import logout
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView

from config.settings import EMAIL_HOST_USER
from users.forms import (
    CustomAuthenticationForm,
    CustomUserCreationForm,
)
from users.models import CustomUser


def UserLogoutView(request):
    logout(request)
    return redirect("meddiag:index")


class UserLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = "login.html"
    success_url = reverse_lazy("meddiag:index")

    def get_success_url(self):
        next_url = self.request.POST.get("next") or self.request.GET.get("next")

        if next_url:
            return next_url

        referer = self.request.META.get("HTTP_REFERER")
        if referer:
            return referer

        return reverse_lazy("meddiag:index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передаем next в контекст для скрытого поля
        context["next"] = self.request.GET.get("next", "")
        return context


def email_verification(request, token):
    user = get_object_or_404(CustomUser, token=token)
    user.is_active = True
    group, created = Group.objects.get_or_create(name="Users")
    user.groups.add(group)
    user.save()
    return redirect(reverse("users:login"))


class RegisterView(FormView):
    model = CustomUser
    template_name = "register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("meddiag:index")

    def form_valid(self, form):
        user = form.save()

        user.is_active = False
        token = secrets.token_hex(16)  # 16 - шкала чисел
        user.token = token
        user.save()

        logout(self.request)

        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}/"
        send_mail(
            subject="Авторизация на сайте",
            message=f"Для завершения регистрации перейдите по ссылке {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )

        return super().form_valid(form)
