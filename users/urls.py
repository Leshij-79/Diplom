from django.urls import path

from users.apps import UsersConfig

from . import views
from .views import (RegisterView, UserDetailView, UserLoginView, UserPasswordResetView, UserProfileView, UsersListView,
                    email_verification, password_confirm, user_active, user_diactive)

app_name = UsersConfig.name

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView, name="logout"),
    path("user/profile/<int:pk>", UserProfileView.as_view(), name="profile"),
    path("users_list/", UsersListView.as_view(), name="users_list"),
    path("user_detail/<int:pk>", UserDetailView.as_view(), name="user_detail"),
    path("user_diactive/<int:pk>", user_diactive, name="user_diactive"),
    path("user_active/<int:pk>", user_active, name="user_active"),
    path("email-confirm/<str:token>/", email_verification, name="email-confirm"),
    path("password_reset/", UserPasswordResetView.as_view(), name="password_reset"),
    path("password_reset/<str:token>/", password_confirm, name="password_confirm"),
]