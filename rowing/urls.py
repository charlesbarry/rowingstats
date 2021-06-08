from django.conf.urls import url, include, re_path
from ajax_select import urls as ajax_select_urls
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView

from . import views
from .views import IndexView, RowerList, RowerDetail, RaceList, RaceDetail, RankingView, AboutView, ClubList, ClubDetail, RowerSearch, CompetitionView, CompetitionResults, RowerCompare, Compare, IndexView2, KnockoutView, WeatherCalc
urlpatterns = [
	#re_path(r'^$', views.current_datetime, name='index'),
	#re_path(r'^recalculate/$', views.CalculateView),
	#re_path(r'^$', views.IndexView.as_view(), name='index'),
	re_path(r'^$', views.IndexView2, name='index'),
	re_path(r'^about/$', views.AboutView.as_view(), name='about'),
	re_path(r'^rowers/$', RowerList.as_view(), name="rower-list"),
	re_path(r'^rowers/(?P<pk>[0-9]+)/$', views.RowerDetail, name="rower-detail"),
	re_path(r'^races/$', RaceList.as_view(), name="race-list"),
	re_path(r'^races/(?P<pk>[0-9]+)/$', views.RaceDetail, name="race-detail"),
	re_path(r'^rankings/$', views.RankingView, name="ranking"),
	re_path(r'^competition/$', views.CompetitionView, name="comp-list"),
	re_path(r'^competition/(?P<pk>[0-9]+)/$', views.CompetitionResults, name="comp-detail"),
	re_path(r'^clubs/$', ClubList.as_view(), name="club-list"),
	re_path(r'^clubs/(?P<pk>[0-9]+)/$', views.ClubDetail, name="club-detail"),
	#re_path(r'^compare/$', csrf_exempt(views.Compare), name="compare-index"),
	re_path(r'^compare/$', views.RowerCompare2, name="compare2"),
	re_path(r'^crewcompare/$', views.CrewCompare, name="crewcompare"),
	re_path(r'^rowing/hrr/(?P<pk>[0-9]+)/$', views.KnockoutView, name="knockouts"),
	re_path(r'^favicon\.ico$',RedirectView.as_view(url='/static/favicon.ico')),
  re_path(r'^weather/$', views.WeatherCalc, name="weather"),
	#re_path(r'^compare/(?P<pk1>[0-9]+)/(?P<pk2>[0-9]+)/$', views.RowerCompare, name="compare"),
	#re_path(r'^rower-autocomplete/$', RowerAutocomplete.as_view(), name="rower-autocomplete"),
	#re_path(r'rowerm2m/$', CrewUpdate.as_view(), name="crew-update"),

	# used in the search function on the rowers view
	re_path(r'^rowersearch/$', views.RowerSearch, name="rower-search"),
	
	# used in autoselect in admin
	re_path(r'^ajax_select/', include(ajax_select_urls)),
]