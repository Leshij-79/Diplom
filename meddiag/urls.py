from django.urls import path

from meddiag.apps import MeddiagConfig
from meddiag.views import IndexListView

app_name = MeddiagConfig.name

urlpatterns = [
    path("", IndexListView.as_view(), name="index"),
]
