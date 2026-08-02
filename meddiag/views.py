from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from icecream import ic

from meddiag.models import Direction, Services
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
        context['doctors'] = self.object.doctors.all()

        return context
