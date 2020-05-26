from django.shortcuts import render

from django.views.generic import ListView, DetailView, UpdateView, TemplateView
from .models import Article
import markdown

# index view: list of all articles
class ArticleList(ListView):
    model = Article
    paginate_by = 5
    ordering = ['-published']
    queryset = Article.objects.filter(public=1)
    
class ArticleDetail2(DetailView):
    model = Article
    
def ArticleDetail(request, pk):
    article = Article.objects.get(pk=pk)
    md = markdown.markdown(article.content)

    return render(request, 'blog/article_detail.html', {'object': article, 'content': md})