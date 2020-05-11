from django.views.generic import ListView, DetailView, UpdateView, TemplateView

class IndexView(TemplateView):
	template_name = 'hrr/index.html'