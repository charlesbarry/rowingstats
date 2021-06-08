from django.conf.urls import url, include, re_path
from ajax_select import urls as ajax_select_urls
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView

from hrr.views import IndexView
urlpatterns = [
	re_path(r'^$', IndexView.as_view(), name='index'),
	#re_path(r'^$', views.IndexView2, name='index'),
]