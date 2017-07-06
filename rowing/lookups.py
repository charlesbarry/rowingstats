from ajax_select import register, LookupChannel
from .models import Rower, Club

@register('crew')
class CrewLookup(LookupChannel):
	model = Rower
	
	def get_query(self, q, request):
		return self.model.objects.filter(name__icontains=q).order_by('name')[:50]
		
	def format_item_display(self, item):
		return "<span class='tag'>%s</span>" % item.name
		
@register('clubs')
class ClubLookup(LookupChannel):
	model = Club
	
	def get_query(self, q, request):
		return self.model.objects.filter(name__icontains=q).order_by('name')[:50]
		
	def format_item_display(self, item):
		return "<span class='tag'>%s</span>" % item.name