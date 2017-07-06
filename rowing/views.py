from django.shortcuts import render
from dal import autocomplete
from django.http import HttpResponse
from django.shortcuts import render
import datetime
from django.core.management import call_command
from django.urls import reverse_lazy

from django.views.generic import ListView, DetailView, UpdateView
from .models import Rower, Race, Result, Competition, Event, Score

def CalculateView(request):
	try:
		call_command('recalculator')
		m = "Recalculations performed successfully."
	except:
		m = "An error occured. Please consult the server logs."
	return render(request, 'rowing/message.html', {'message': m})

def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)
	
class IndexView(ListView):
	template_name = 'rowing/index.html'
	
class RowerList(ListView):
	model = Rower
	paginate_by = 30
	ordering = ['name']
	
class RowerDetail(DetailView):
	model = Rower
	
class RaceList(ListView):
	model = Race
	paginate_by = 30
	ordering = ['name']
	
class RaceDetail(DetailView):
	model = Race
	
# in progress
# Want /races to go to list of competitions
# Want /races/1 to go to list of all Races for that competition, with filters by event
class CompetitionList(ListView):
	model = Competition
	paginate_by = 30
	ordering = ['name']
'''	
# a test which is purely for education
def test_form(request):
	# if GET, return a blank form. if POST, process the data
	if request.method == "POST":
		# fill the form with the submitted data
		form = NameForm(request.POST)
		
		# check for validity, if so do stuff
		if form.is_valid():
			# NB data is now stored in form.cleaned_data (a dict)
			
			
			# shove the person on to the next page
			return HttpResponseRedirect('/landing/')
			
		#if using ModelForm, no need to use validator above - done on save
		# if commit == False, data will not be saved immediately, but object will be manipulable
		new_record = form.save(commit=True)
		
		# if many to many data exists, this step is necessary if commit==False to add after record is saved
		form.save_m2m()
		
		return HttpResponseRedirect('/landing/')
			
	else:
			#serve a blank form
			form = NameForm()
		
		# pass the blank form to the template
		# NB the template needs to have <form></form> wrapper around {{form}} and the submit mechanism made clear
		return render(request, 'template.html', {'form':form})
'''		
class RankingList(ListView):
	queryset = Rower.objects.all()
	template_name = 'test'
	ordering = ['sweep_mu']