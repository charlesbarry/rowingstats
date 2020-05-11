from django.conf.urls import url, include
from ajax_select import urls as ajax_select_urls
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView

from hrr.views import IndexView
urlpatterns = [
	url(r'^$', IndexView.as_view(), name='index'),
	#url(r'^$', views.IndexView2, name='index'),
]