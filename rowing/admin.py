from django.contrib import admin
from ajax_select import make_ajax_form
from ajax_select.fields import autoselect_fields_check_can_add
from ajax_select.admin import AjaxSelectAdminTabularInline, AjaxSelectAdminStackedInline

# Register your models here.
from .models import Rower, Race, Result, Competition, Event, Club, Time, Fixture, KnockoutRace, Alias, ClubAlias, RaceLink
from .forms import ResultForm

class TimeInline(admin.TabularInline):
	model = Time
	extra = 0

# custom admin to allow ajax many 2 many selection for crew members
class ResultAdmin(admin.ModelAdmin):
	form = ResultForm
	inlines = [TimeInline]
	raw_id_fields = ("race",)
	
	# creates the add function
	def get_form(self, request, obj=None, **kwargs):
		form = super(ResultAdmin, self).get_form(request, obj, **kwargs)
		autoselect_fields_check_can_add(form, self.model, request.user)
		return form
		
class ResultInline(AjaxSelectAdminTabularInline):
	model = Result
	form = ResultForm
	extra = 0
	show_change_link = True
	
	# REDUNDANT - creates the add function
	'''def get_form(self, request, obj=None, **kwargs):
		form = super(ResultInline, self).get_form(request, obj, **kwargs)
		autoselect_fields_check_can_add(form, self.model, request.user)
		return form'''

class KRInline(admin.TabularInline):
	model = KnockoutRace
	fields = ['bye', 'margin']
		
class RaceAdmin(admin.ModelAdmin):
	model = Race
	list_display = ['name', 'get_event', 'date']
	inlines = [ResultInline, KRInline]
	list_filter = ['event__comp__name']
	search_fields = ['name']
	
	def get_event(self, obj):
		return obj.event.name
	get_event.short_description = 'Event'
	get_event.admin_order_field = 'event__name'
	
	'''def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "name"'''
	
class RowerAdmin(admin.ModelAdmin):
	model = Rower
	list_display = ['name', 'gender', 'nationality']
	list_filter = ['gender', 'nationality']
	search_fields = ['name']
	
class TimeAdmin(admin.ModelAdmin):
	raw_id_fields = ("result",)
	
class RaceLinkAdmin(admin.ModelAdmin):
	raw_id_fields = ("startrace","endrace")
	
class KRAdmin(admin.ModelAdmin):
	raw_id_fields = ("race","child")
	list_filter = ['knockout']
	
class EventAdmin(admin.ModelAdmin):
	model = Event
	search_fields = ['name']
	list_display = ['name', 'comp', 'type']
	list_filter = ['comp', 'type']
	
class ClubAdmin(admin.ModelAdmin):
	model = Club
	search_fields = ['name']

class AliasAdmin(admin.ModelAdmin):
	model = Alias
	raw_id_fields = ("rower",)

admin.site.register(Rower, RowerAdmin)
admin.site.register(Race, RaceAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Competition)
admin.site.register(Event, EventAdmin)
admin.site.register(Fixture)
admin.site.register(Club, ClubAdmin)
admin.site.register(ClubAlias)
admin.site.register(RaceLink, RaceLinkAdmin)
admin.site.register(Alias, AliasAdmin)
admin.site.register(Time, TimeAdmin)
admin.site.register(KnockoutRace, KRAdmin)