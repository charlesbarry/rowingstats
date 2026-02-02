from django.shortcuts import render, get_object_or_404
from django.utils.html import escape
import bleach

from django.views.generic import ListView, DetailView, UpdateView, TemplateView
from .models import Article
import markdown

# Allowed HTML tags for sanitized markdown output
ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'br', 'code', 'div', 'em',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'li', 'ol', 'p',
    'pre', 'span', 'strong', 'table', 'tbody', 'td', 'th', 'thead', 'tr', 'ul',
]
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel'],
    'img': ['src', 'alt', 'title'],
    'abbr': ['title'],
    'acronym': ['title'],
}

# index view: list of all articles
class ArticleList(ListView):
    model = Article
    paginate_by = 5
    ordering = ['-published']
    queryset = Article.objects.filter(public=1)

class ArticleDetail2(DetailView):
    model = Article

def ArticleDetail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    # Render markdown and then sanitize HTML to prevent XSS
    md_html = markdown.markdown(article.content)
    safe_html = bleach.clean(md_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)

    return render(request, 'blog/article_detail.html', {'object': article, 'content': safe_html})