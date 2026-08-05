from django.conf.urls.static import static
from django.urls import path

from config import settings
from meddiag.apps import MeddiagConfig
from meddiag.views import (
    AboutView,
    AppointmentCancelView,
    AppointmentCreateView,
    AppointmentDetailView,
    AppointmentSuccessView,
    ContactFormSuccessView,
    ContactFormView,
    ContactsView,
    DoctorDetailView,
    DoctorsListView,
    IndexListView,
    ProfileView,
    ServiceDetailView,
    ServicesListView,
)

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
    path("appointment/<int:pk>/", AppointmentDetailView.as_view(), name="appointment_detail"),
    path("appointment/cancel/<int:pk>/", AppointmentCancelView.as_view(), name="appointment_cancel"),
    path("appointment/success/", AppointmentSuccessView.as_view(), name="appointment_success"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("about/", AboutView.as_view(), name="about"),
    path("contacts/", ContactsView.as_view(), name="contacts"),
    path("contact-form/", ContactFormView.as_view(), name="contact_form"),
    path("contact-form/success/", ContactFormSuccessView.as_view(), name="contact_form_success"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
