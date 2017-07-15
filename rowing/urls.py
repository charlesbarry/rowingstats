from django.conf.urls import url, include
from ajax_select import urls as ajax_select_urls

from . import views
from .views import IndexView, RowerList, RowerDetail, RaceList, RaceDetail, RankingView, AboutView, ClubList, ClubDetail, RowerSearch
urlpatterns = [
	#url(r'^$', views.current_datetime, name='index'),
	#url(r'^recalculate/$', views.CalculateView),
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^about/$', views.AboutView.as_view(), name='index'),
	url(r'^rowers/$', RowerList.as_view(), name="rower-list"),
	url(r'^rowers/(?P<pk>[0-9]+)/$', views.RowerDetail, name="rower-detail"),
	url(r'^races/$', RaceList.as_view(), name="race-list"),
	url(r'^races/(?P<pk>[0-9]+)/$', views.RaceDetail, name="race-detail"),
	url(r'^rankings/$', views.RankingView, name="ranking"),
	url(r'^clubs/$', ClubList.as_view(), name="club-list"),
	url(r'^clubs/(?P<pk>[0-9]+)/$', ClubDetail.as_view(), name="club-list"),
	#url(r'^rower-autocomplete/$', RowerAutocomplete.as_view(), name="rower-autocomplete"),
	#url(r'rowerm2m/$', CrewUpdate.as_view(), name="crew-update"),
	
	url(r'^rowersearch/$', views.RowerSearch, name="rower-search"),
	
	#used in autoselect?
	url(r'^ajax_select/', include(ajax_select_urls)),
]