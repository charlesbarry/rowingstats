from django.contrib import admin
from ajax_select import make_ajax_form
from ajax_select.fields import autoselect_fields_check_can_add

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
		
class ResultInline(admin.TabularInline):
	model = Result
	form = ResultForm
	extra = 0
	
	# creates the add function
	def get_form(self, request, obj=None, **kwargs):
		form = super(ResultInline, self).get_form(request, obj, **kwargs)
		autoselect_fields_check_can_add(form, self.model, request.user)
		return form
	
class RaceAdmin(admin.ModelAdmin):
	model = Race
	list_display = ['name', 'date']
	inlines = [ResultInline]
	list_filter = ['event__comp__name']
	#BROKEN: list_filter = (('event', admin.RelatedOnlyFieldListFilter))

admin.site.register(Rower)
admin.site.register(Race, RaceAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Competition)
admin.site.register(Event)
admin.site.register(Club)