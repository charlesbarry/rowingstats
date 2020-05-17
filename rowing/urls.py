from django.conf.urls import url, include
from ajax_select import urls as ajax_select_urls
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView

from . import views
from .views import IndexView, RowerList, RowerDetail, RaceList, RaceDetail, RankingView, AboutView, ClubList, ClubDetail, RowerSearch, CompetitionView, CompetitionResults, RowerCompare, Compare, IndexView2, KnockoutView
urlpatterns = [
	#url(r'^$', views.current_datetime, name='index'),
	#url(r'^recalculate/$', views.CalculateView),
	#url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^$', views.IndexView2, name='index'),
	url(r'^about/$', views.AboutView.as_view(), name='about'),
	url(r'^rowers/$', RowerList.as_view(), name="rower-list"),
	url(r'^rowers/(?P<pk>[0-9]+)/$', views.RowerDetail, name="rower-detail"),
	url(r'^races/$', RaceList.as_view(), name="race-list"),
	url(r'^races/(?P<pk>[0-9]+)/$', views.RaceDetail, name="race-detail"),
	url(r'^rankings/$', views.RankingView, name="ranking"),
	url(r'^competition/$', views.CompetitionView, name="comp-list"),
	url(r'^competition/(?P<pk>[0-9]+)/$', views.CompetitionResults, name="comp-detail"),
	url(r'^clubs/$', ClubList.as_view(), name="club-list"),
	url(r'^clubs/(?P<pk>[0-9]+)/$', views.ClubDetail, name="club-detail"),
	#url(r'^compare/$', csrf_exempt(views.Compare), name="compare-index"),
	url(r'^compare/$', views.RowerCompare2, name="compare2"),
	url(r'^crewcompare/$', views.CrewCompare, name="crewcompare"),
	url(r'^rowing/hrr/(?P<pk>[0-9]+)/$', views.KnockoutView, name="knockouts"),
	url(r'^favicon\.ico$',RedirectView.as_view(url='/static/favicon.ico')),
	#url(r'^compare/(?P<pk1>[0-9]+)/(?P<pk2>[0-9]+)/$', views.RowerCompare, name="compare"),
	#url(r'^rower-autocomplete/$', RowerAutocomplete.as_view(), name="rower-autocomplete"),
	#url(r'rowerm2m/$', CrewUpdate.as_view(), name="crew-update"),
	
	# used in the search function on the rowers view
	url(r'^rowersearch/$', views.RowerSearch, name="rower-search"),
	
	# used in autoselect in admin
	url(r'^ajax_select/', include(ajax_select_urls)),
]