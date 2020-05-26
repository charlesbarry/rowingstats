from django.conf.urls import url, include
#from django.views.decorators.csrf import csrf_exempt

from . import views
from .views import ArticleList, ArticleDetail
urlpatterns = [
    url(r'^$', ArticleList.as_view(), name='blog-index'),
    url(r'^(?P<pk>[0-9]+)/$', ArticleDetail, name='blog-detail')
]