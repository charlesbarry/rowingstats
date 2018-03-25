from django.contrib import admin
from ajax_select import make_ajax_form
from ajax_select.fields import autoselect_fields_check_can_add
from ajax_select.admin import AjaxSelectAdminTabularInline, AjaxSelectAdminStackedInline

# Register your models here.
from .models import Rower, Race, Result, Competition, Event, Club
from .forms import ResultForm

# custom admin to allow ajax many 2 many selection for crew members
class ResultAdmin(admin.ModelAdmin):
	form = ResultForm
	
	# creates the add function
	def get_form(self, request, obj=None, **kwargs):
		form = super(ResultAdmin, self).get_form(request, obj, **kwargs)
		autoselect_fields_check_can_add(form, self.model, request.user)
		return form
		
class ResultInline(AjaxSelectAdminTabularInline):
	model = Result
	form = ResultForm
	extra = 0
	
	# REDUNDANT - creates the add function
	'''def get_form(self, request, obj=None, **kwargs):
		form = super(ResultInline, self).get_form(request, obj, **kwargs)
		autoselect_fields_check_can_add(form, self.model, request.user)
		return form'''
	
class RaceAdmin(admin.ModelAdmin):
	model = Race
	list_display = ['name', 'get_event', 'date']
	inlines = [ResultInline]
	list_filter = ['event__comp__name']
	#BROKEN: list_filter = (('event', admin.RelatedOnlyFieldListFilter))
	
	def get_event(self, obj):
		return obj.event.name
	get_event.short_description = 'Event'
	get_event.admin_order_field = 'event__name'
	
	'''def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "name"'''
	
class RowerAdmin(admin.ModelAdmin):
	model = Race
	list_display = ['name', 'gender', 'nationality']
	#list_filter = ['name']

admin.site.register(Rower, RowerAdmin)
admin.site.register(Race, RaceAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Competition)
admin.site.register(Event)
admin.site.register(Club)