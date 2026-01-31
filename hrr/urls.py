from django.urls import re_path

from hrr.views import IndexView
urlpatterns = [
	re_path(r'^$', IndexView.as_view(), name='index'),
	#re_path(r'^$', views.IndexView2, name='index'),
]