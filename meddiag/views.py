from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
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
