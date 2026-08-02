from django.conf.urls.static import static
from django.urls import path

from config import settings
from meddiag.apps import MeddiagConfig
from meddiag.views import IndexListView, ServicesListView, ServiceDetailView

app_name = MeddiagConfig.name

urlpatterns = [
    path("", IndexListView.as_view(), name="index"),
    path("services/", ServicesListView.as_view(), name="services_list"),
    path("service/<int:pk>/", ServiceDetailView.as_view(), name="service_detail"),
    path("services/<int:pk>/", ServicesListView.as_view(), name="services_list_index"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
