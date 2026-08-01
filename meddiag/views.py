from django.views.generic import ListView

from meddiag.models import Direction, Services


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
        return Services.objects.select_related('direction').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['direction'] = Direction.objects.all()
        return context

