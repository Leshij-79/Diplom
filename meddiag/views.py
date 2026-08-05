import json
from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView

from config.settings import EMAIL_HOST_USER
from meddiag.forms import AppointmentForm, ContactForm
from meddiag.mixins import CompanyInfoMixin
from meddiag.models import AboutCompany, Appointment, Contacts, Direction, Doctors, Services


class IndexListView(CompanyInfoMixin, ListView):
    model = Direction
    template_name = "index.html"

    def get_queryset(self):
        return Direction.objects.all()


class DirectionListView(CompanyInfoMixin, ListView):
    pass


class ServicesListView(CompanyInfoMixin, ListView):
    model = Services
    template_name = "services_list.html"
    context_object_name = "services_list"

    def get_queryset(self):
        queryset = Services.objects.select_related("direction").all()
        direction_id = self.kwargs.get("pk")

        if direction_id:
            queryset = queryset.filter(direction=direction_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["directions"] = Direction.objects.all()

        # Добавляем ID текущей категории
        direction_id = self.kwargs.get("pk")
        context["current_category_id"] = direction_id

        # Добавляем текущую категорию для отображения названия
        if direction_id:
            try:
                context["current_direction"] = Direction.objects.get(pk=direction_id)
            except Direction.DoesNotExist:
                context["current_direction"] = None
        else:
            context["current_direction"] = None

        return context


class ServiceDetailView(CompanyInfoMixin, DetailView):
    model = Services
    template_name = "service_detail.html"
    context_object_name = "service"
    success_url = reverse_lazy("meddiag:services_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor_id = self.request.GET.get("doctor_id")

        if doctor_id:
            try:
                context["doctors"] = self.object.doctors.filter(pk=doctor_id)
                context["from_doctor_page"] = True
                context["doctor_id"] = doctor_id
            except Doctors.DoesNotExist:
                context["doctors"] = self.object.doctors.all()
                context["from_doctor_page"] = False
        else:
            context["doctors"] = self.object.doctors.all()
            context["from_doctor_page"] = False

        return context


class DoctorsListView(CompanyInfoMixin, ListView):
    model = Doctors
    template_name = "doctors_list.html"
    context_object_name = "doctors_list"

    def get_queryset(self):
        queryset = Doctors.objects.select_related("direction").all()
        direction_id = self.kwargs.get("pk")

        if direction_id:
            queryset = queryset.filter(direction=direction_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["directions"] = Direction.objects.all()

        direction_id = self.kwargs.get("pk")
        context["current_direction_id"] = direction_id

        if direction_id:
            try:
                context["current_direction"] = Direction.objects.get(pk=direction_id)
            except Direction.DoesNotExist:
                context["current_direction"] = None
        else:
            context["current_direction"] = None

        return context


class DoctorDetailView(CompanyInfoMixin, DetailView):
    model = Doctors
    template_name = "doctor_detail.html"
    context_object_name = "doctor"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_id = self.request.GET.get("service_id")

        if service_id:
            try:
                context["services"] = Services.objects.filter(pk=service_id)
                context["from_service_page"] = True
                context["service_id"] = service_id
            except Services.DoesNotExist:
                context["services"] = self.object.doctors_service.all()
                context["from_service_page"] = False
        else:
            context["services"] = self.object.doctors_service.all()
            context["from_service_page"] = False

        return context


class AppointmentCreateView(CompanyInfoMixin, LoginRequiredMixin, FormView):
    template_name = "appointment_create.html"
    form_class = AppointmentForm
    success_url = reverse_lazy("meddiag:appointment_success")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["services"] = Services.objects.all().select_related("direction")

        service_id = self.request.GET.get("service") or self.request.POST.get("service")
        if service_id:
            try:
                context["selected_service"] = Services.objects.get(pk=service_id)
            except Services.DoesNotExist:
                pass

        doctor_id = self.request.GET.get("doctor") or self.request.POST.get("doctor")
        if doctor_id:
            try:
                context["selected_doctor"] = Doctors.objects.get(pk=doctor_id)
            except Doctors.DoesNotExist:
                pass

        doctor_for_service = {}
        for service in context["services"]:
            doctors = service.doctors.all()
            doctor_list = []  # Создаем список для каждого сервиса

            for doctor in doctors:
                doctor_list.append(
                    {
                        "id": doctor.id,
                        "last_name": doctor.last_name,
                        "first_name": doctor.first_name,
                        "middle_name": doctor.middle_name,
                        "specialization": doctor.specialization,
                    }
                )

            # Добавляем список врачей для этого сервиса
            doctor_for_service[str(service.id)] = doctor_list

        context["doctor_for_service"] = json.dumps(doctor_for_service)

        context["date"] = date.today().isoformat()

        if self.request.method == "POST":
            context["selected_date"] = self.request.POST.get("date")
            context["selected_time"] = self.request.POST.get("time")
            context["comment"] = self.request.POST.get("comment")

        context["from_service"] = self.request.GET.get("from_service")
        context["from_doctor"] = self.request.GET.get("from_doctor")

        return context

    def form_valid(self, form):
        service_id = self.request.POST.get("services")
        doctor_id = self.request.POST.get("doctor")
        appointment_datetime = form.cleaned_data.get("datetime")
        service = get_object_or_404(Services, pk=service_id)
        doctor = get_object_or_404(Doctors, pk=doctor_id)
        contacts = Contacts.objects.first()

        if not all([service, doctor, appointment_datetime]):
            messages.error(self.request, "Пожалуйста, заполните все поля")
            return self.form_invalid(form)

        try:

            # if appointment_datetime.hour < 8 or appointment_datetime.hour > 20:
            if appointment_datetime.hour < int(contacts.hour_start) or appointment_datetime.hour > int(
                contacts.hour_end
            ):
                messages.error(self.request, "Выбрано не рабочее время")
                return self.form_invalid(form)

            if appointment_datetime.date() < datetime.now().date():
                messages.error(self.request, "Выбрана прошедшая дата")
                return self.form_invalid(form)

            exist_appointment = Appointment.objects.filter(
                doctor=doctor, datetime=appointment_datetime, status="active"
            ).exists()

            if exist_appointment:
                messages.error(self.request, "Это время занято")
                return self.form_invalid(form)

            appointment = Appointment(
                patient=self.request.user,
                doctor=doctor,
                services=service,
                datetime=appointment_datetime,
                status="active",
            )

            appointment.save()
            message_information = (
                f"Вы успешно записались к врачу {doctor.last_name} {doctor.first_name} "
                f"{doctor.middle_name} на {service.name} в "
                f'{appointment_datetime.strftime("%d.%m.%Y %H:%M")}'
            )
            messages.success(self.request, message_information)

            user = self.request.user
            send_mail(
                subject="Запись на приём",
                message=message_information,
                from_email=EMAIL_HOST_USER,
                recipient_list=[user.email],
            )

            return redirect(self.success_url)

        except (Services.DoesNotExist, Doctors.DoesNotExist):
            messages.error(self.request, "Выбранная услуга или врач не найдены.")
            return self.form_invalid(form)

        except ValueError:
            messages.error(self.request, f"Неверный формат даты или времени. {ValueError}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_initial(self):
        initial = super().get_initial()

        # Получаем параметры из GET-запроса
        service_id = self.request.GET.get("service")
        doctor_id = self.request.GET.get("doctor")

        if service_id:
            try:
                service = Services.objects.get(pk=service_id)
                initial["services"] = service.id
            except Services.DoesNotExist:
                pass

        if doctor_id:
            try:
                doctor = Doctors.objects.get(pk=doctor_id)
                initial["doctor"] = doctor.id
            except Doctors.DoesNotExist:
                pass

        return initial


class AppointmentSuccessView(CompanyInfoMixin, LoginRequiredMixin, TemplateView):
    template_name = "appointment_success.html"


class ProfileView(CompanyInfoMixin, LoginRequiredMixin, TemplateView):
    model = Appointment
    template_name = "profile.html"
    context_object_name = "profile"
    success_url = reverse_lazy("meddiag:profile")

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["appointments_active"] = (
            Appointment.objects.filter(patient=self.request.user).exclude(status="cancel").exclude(status="rendered")
        )
        context["appointment_archive"] = Appointment.objects.filter(patient=self.request.user).exclude(status="active")

        return context


class AppointmentDetailView(CompanyInfoMixin, LoginRequiredMixin, DetailView):
    model = Appointment
    template_name = "appointment_detail.html"
    context_object_name = "appointment_detail"

    def get_queryset(self):
        return Appointment.objects.filter(patient=self.request.user)


class AppointmentCancelView(CompanyInfoMixin, LoginRequiredMixin, TemplateView):
    model = Appointment
    template_name = "appointment_cancel.html"
    context_object_name = "appointment_cancel"

    def post(self, request, *args, **kwargs):
        appointment = get_object_or_404(Appointment, patient=self.request.user, pk=kwargs["pk"])

        if appointment.status == "active":
            appointment.status = "cancel"
            appointment.save()
            messages.success(request, "Запись успешно отменена")
        else:
            messages.error(request, "Запись уже отменена или оказана")

        message_information = (
            f"Вы успешно отменили запись к врачу {appointment.doctor.last_name} "
            f"{appointment.doctor.first_name} {appointment.doctor.middle_name} на "
            f'{appointment.services.name} в {appointment.datetime.strftime("%d.%m.%Y %H:%M")}'
        )
        messages.success(self.request, message_information)

        user = self.request.user
        send_mail(
            subject="Отмена записи на приём",
            message=message_information,
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )

        return redirect("meddiag:appointment_detail", pk=appointment.pk)


class AboutView(CompanyInfoMixin, TemplateView):
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["about"] = AboutCompany.objects.first()
        return context


class ContactsView(CompanyInfoMixin, TemplateView):
    template_name = "contacts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contacts"] = Contacts.objects.first()
        return context


class ContactFormView(CompanyInfoMixin, FormView):
    template_name = "contact_form.html"
    form_class = ContactForm
    success_url = reverse_lazy("meddiag:contact_form_success")

    def form_valid(self, form):
        name = form.cleaned_data.get("name")
        email = form.cleaned_data.get("email")
        phone = form.cleaned_data.get("phone", "Не указан")
        subject = form.cleaned_data.get("subject")
        message = form.cleaned_data.get("message")

        contacts = Contacts.objects.first()
        about_company = AboutCompany.objects.first()
        to_email = contacts.email

        subject_type = {
            "appointment": "Запись на прием",
            "question": "Вопрос по услугам",
            "complaint": "Жалоба или предложение",
            "cooperation": "Сотрудничество",
            "other": "Другое",
        }

        subject_text = subject_type[subject]
        message_text = (
            f"От: {name},\n"
            f"Email: {email},\n"
            f"Телефон: {phone},\n"
            f"Тема: {subject_text},\n"
            f"Сообщение: {message}\n"
        )

        send_mail(
            subject="Сообщение с формы обратной связи",
            message=message_text,
            from_email=EMAIL_HOST_USER,
            recipient_list=[to_email],
        )

        message_information = (
            f"Здравствуйте, {name}.\n\n"
            f"Вы отправили вообщение\n\n"
            f"{message_text}\n\n"
            f"Спасибо за обращение. При необходимости мы свяжемся с вами"
        )

        send_mail(
            subject=f"Копия вашего обращения в {about_company.small_name}",
            message=message_information,
            from_email=EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(self.request, "Ваше сообщение успешно отправлено! " "Мы свяжемся с вами в ближайшее время.")

        return super().form_valid(form)


class ContactFormSuccessView(CompanyInfoMixin, TemplateView):
    template_name = "contact_form_success.html"
