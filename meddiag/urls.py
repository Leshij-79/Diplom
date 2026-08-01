from django.conf.urls.static import static
from django.urls import path

from config import settings
from meddiag.apps import MeddiagConfig
from meddiag.views import IndexListView, ServicesListView

app_name = MeddiagConfig.name

urlpatterns = [
    path("", IndexListView.as_view(), name="index"),
    path("services/<int:pk>/", ServicesListView.as_view(), name="services_list"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
