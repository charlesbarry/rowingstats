from django.shortcuts import render

from django.views.generic import ListView, DetailView, UpdateView, TemplateView
from .models import Article

# index view: list of all articles
class ArticleList(ListView):
	model = Article
	paginate_by = 5
	ordering = ['-published']
	
class ArticleDetail(DetailView):
	model = Article

# detail view: detail of item