from django.conf.urls.static import static
from django.urls import path

from config import settings
from meddiag.apps import MeddiagConfig
from meddiag.views import IndexListView, ServicesListView, ServiceDetailView, DoctorsListView, DoctorDetailView, \
    AppointmentCreateView, AppointmentSuccessView

app_name = MeddiagConfig.name

urlpatterns = [
    path("", IndexListView.as_view(), name="index"),
    path("services/", ServicesListView.as_view(), name="services_list"),
    path("service/<int:pk>/", ServiceDetailView.as_view(), name="service_detail"),
    path("services/<int:pk>/", ServicesListView.as_view(), name="services_list_index"),
    path("doctors/", DoctorsListView.as_view(), name="doctors_list"),
    path("doctors/<int:pk>/", DoctorsListView.as_view(), name="doctors_list_direction"),
    path("doctor/<int:pk>/", DoctorDetailView.as_view(), name="doctor_detail"),
    path("appointment/create/", AppointmentCreateView.as_view(), name="appointment_create"),
    path("appointment/success/", AppointmentSuccessView.as_view(), name="appointment_success"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
