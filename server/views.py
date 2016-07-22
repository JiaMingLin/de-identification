
from django.views import generic
from django.shortcuts import redirect

class IndexView(generic.ListView):
	template_name = 'Dashboard.html'

	def get_queryset(self):
		pass

def home(request):
	return redirect('/privacy/')