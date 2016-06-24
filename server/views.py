
from django.views import generic

class IndexView(generic.ListView):
    template_name = 'Dashboard.html'

    def get_queryset(self):
        pass