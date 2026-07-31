from django.views.generic import ListView

from meddiag.models import Direction


class IndexListView(ListView):
    model = Direction
    template_name = 'index.html'

    def get_queryset(self):
        return Direction.objects.all()
