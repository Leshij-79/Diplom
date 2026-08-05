from django.urls import path

from users.apps import UsersConfig

from . import views
from .views import RegisterView, UserLoginView, email_verification

app_name = UsersConfig.name

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView, name="logout"),
    path("email-confirm/<str:token>/", email_verification, name="email-confirm"),
]
