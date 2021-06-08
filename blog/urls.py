from django.conf.urls import url, include, re_path
#from django.views.decorators.csrf import csrf_exempt

from . import views
from .views import ArticleList, ArticleDetail
urlpatterns = [
    re_path(r'^$', ArticleList.as_view(), name='blog-index'),
    re_path(r'^(?P<pk>[0-9]+)/$', ArticleDetail, name='blog-detail')
]