import json
from datetime import date, datetime
from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, FormView
from icecream import ic

from meddiag.models import Direction, Services, Doctors
from meddiag.services import ServicesServices


class IndexListView(ListView):
    model = Direction
    template_name = 'index.html'

    def get_queryset(self):
        return Direction.objects.all()


class DirectionListView(ListView):
    pass


class ServicesListView(ListView):
    model = Services
    template_name = 'services_list.html'
    context_object_name = 'services_list'

    def get_queryset(self):
        queryset = Services.objects.select_related('direction').all()
        direction_id = self.kwargs.get('pk')

        if direction_id:
            queryset = queryset.filter(direction=direction_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['directions'] = Direction.objects.all()

        # Добавляем ID текущей категории
        direction_id = self.kwargs.get('pk')
        context['current_category_id'] = direction_id

        # Добавляем текущую категорию для отображения названия
        if direction_id:
            try:
                context['current_direction'] = Direction.objects.get(pk=direction_id)
            except Direction.DoesNotExist:
                context['current_direction'] = None
        else:
            context['current_direction'] = None

        return context


class ServiceDetailView(DetailView):
    model = Services
    template_name = 'service_detail.html'
    context_object_name = "service"
    success_url = reverse_lazy("meddiag:services_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor_id = self.request.GET.get('doctor_id')

        if doctor_id:
            try:
                context['doctors'] = self.object.doctors.filter(pk=doctor_id)
                context['from_doctor_page'] = True
                context['doctor_id'] = doctor_id
            except Doctors.DoesNotExist:
                context['doctors'] = self.object.doctors.all()
                context['from_doctor_page'] = False
        else:
            context['doctors'] = self.object.doctors.all()
            context['from_doctor_page'] = False

        return context


class DoctorsListView(ListView):
    model = Doctors
    template_name = 'doctors_list.html'
    context_object_name = 'doctors_list'

    def get_queryset(self):
        queryset = Doctors.objects.select_related('direction').all()
        direction_id = self.kwargs.get('pk')

        if direction_id:
            queryset = queryset.filter(direction=direction_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['directions'] = Direction.objects.all()

        direction_id = self.kwargs.get('pk')
        context['current_direction_id'] = direction_id

        if direction_id:
            try:
                context['current_direction'] = Direction.objects.get(pk=direction_id)
            except Direction.DoesNotExist:
                context['current_direction'] = None
        else:
            context['current_direction'] = None

        return context


class DoctorDetailView(DetailView):
    model = Doctors
    template_name = 'doctor_detail.html'
    context_object_name = 'doctor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        services = self.object.doctors_service.all()
        context['services'] = services

        # Получаем услуги, которые оказывает врач
        # context['services'] = self.object.doctors_service.all()

        return context


class AppointmentCreateView(LoginRequiredMixin, FormView):
    template_name = 'appointment_create.html'
    success_url = reverse_lazy('meddiag:appointment_success')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['services'] = Services.objects.all().select_related('direction')

        service_id = self.request.GET.get('service') or self.request.POST.get('service')
        if service_id:
            try:
                context['select_service'] = Services.objects.get(pk=service_id)
            except Services.DoesNotExist:
                pass

        doctor_id = self.request.GET.get('doctor_id') or self.request.POST.get('doctor_id')
        if doctor_id:
            try:
                context['select_doctor'] = Doctors.objects.get(pk=doctor_id)
            except Doctors.DoesNotExist:
                pass

        doctor_for_service = {}
        for service in context['select_service']:
            doctors = service.doctors.all()

            for doctor in doctors:
                doctor_for_service[str(service.id)] = [
                    {
                        'id': doctor.id,
                        'last_name': doctor.last_name,
                        'first_name': doctor.first_name,
                        'middle_name': doctor.middle_name,
                        'specialization': doctor.specialization,
                    }
                ]

            context['doctor_for_service'] = json.dumps(doctor_for_service)

            context['date'] = date.today().isoformat()

            if self.request.method == 'POST':
                context['selected_date'] = self.request.POST.get('date')
                context['selected_time'] = self.request.POST.get('time')
                context['comment'] = self.request.POST.get('comment')

            context['from_service'] = self.request.GET.get('from_service')
            context['from_doctor'] = self.request.GET.get('from_doctor')

        return context

    def form_valid(self, form):
        service_id = form.request.POST.get('service')
        doctor_id = form.request.POST.get('doctor')
        date_str = self.request.POST.get('date')
        time_str = self.request.POST.get('time')
        comment = self.request.POST.get('comment')

        if not all([service_id, doctor_id, date_str, time_str, comment]):
            messages.error(self.request, 'Пожалуйста, заполните все поля')
            return self.form_invalid(form)

        try:
            service = get_object_or_404(Services, pk=service_id)
            doctor = get_object_or_404(Doctors, pk=doctor_id)
            datetime_str = f"{date_str} {time_str}"
            appointment_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

#TODO: поставить время из таблицы настроек

            if appointment_datetime.hour < 8 or appointment_datetime.hour > 20:
                messages.error(self.request, '')
