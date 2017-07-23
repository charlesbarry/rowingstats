from django.shortcuts import render
#from dal import autocomplete
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
import datetime
from django.core.management import call_command
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from itertools import groupby
from scipy.stats import norm

from django.views.generic import ListView, DetailView, UpdateView, TemplateView
from .models import Rower, Race, Result, Competition, Event, Score, Club, ScoreRanking
from .forms import CompareForm, RankingForm

# only used in development
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
	
class IndexView(TemplateView):
	template_name = 'rowing/index.html'
	
class AboutView(TemplateView):
	template_name = 'rowing/about.html'
	
''' class RowerList(ListView):
	model = Rower
	paginate_by = 50
	ordering = ['name']'''
	
class RowerList(TemplateView):
	template_name = 'rowing/rower_list.html'
	
def RowerSearch(request):
	if request.method == 'GET' and 'q' in request.GET:
		#q = request.GET.get('q', None)
		q = request.GET['q']
		
		if q:
			results = Rower.objects.filter(name__icontains=q)[:20]
			context = {'results': results}
		else:
			context = {}
	
	else:
		context = {}
	
	return render(request, 'rowing/rower_search.html', context)
	
def RowerDetail(request, pk):
	context = {}
	ptype = request.GET.get('type','Sweep')
	
	r1 = Rower.objects.get(pk=pk)
	context['object'] = r1
	context['jsuplist'] = []
	context['jsmulist']	= []
	context['jslolist'] = []
	try:
		context['scores'] = r1.score_set.filter(result__race__event__type=ptype).order_by('-result__race__date', '-result__race__order')
		context['rscores'] = r1.score_set.filter(result__race__event__type=ptype).order_by('result__race__date', 'result__race__order')
		
		# adds the count for the position
		for item in context['scores']:
			item.total_pos = len(Result.objects.filter(race__id=item.result.race.pk))
		
		# generates chart data
		for k, group in groupby(context['rscores'], key = lambda x: x.result.race.date):
			item2 = ""
			for item2 in group:
				pass
			
			context['jsuplist'].append([item2.result.race.date, (item2.mu+item2.sigma)])
			context['jsmulist'].append([item2.result.race.date, item2.mu])
			context['jslolist'].append([item2.result.race.date, (item2.mu-item2.sigma)])
		
	except ObjectDoesNotExist:
		context['scores'] = None
	#context['clubs'] = r1.result_set.all()
	
	return render(request, 'rowing/rower_detail.html', context)
	


def RowerCompare(request, pk1, pk2):
	ptype = request.GET.get('type','Sweep')
	context = {}
	context['type'] = ptype
	context['jsmulist1'] = []
	context['jsmulist2'] = []
	try:
		#get their latest scores
		r1 = Rower.objects.get(pk=pk1)
		r2 = Rower.objects.get(pk=pk2)
		context['rower1'] = r1
		context['rower2'] = r2
		
		try: 
			context['rscores1'] = r1.score_set.filter(result__race__event__type=ptype).order_by('result__race__date', 'result__race__order')
			context['rscores2'] = r2.score_set.filter(result__race__event__type=ptype).order_by('result__race__date', 'result__race__order')
			
			# generates chart data
			for k, group in groupby(context['rscores1'], key = lambda x: x.result.race.date):
				item = ""
				for item in group:
					pass
				
				context['jsmulist1'].append([item.result.race.date, item.mu])
				
			for k, group in groupby(context['rscores2'], key = lambda x: x.result.race.date):
				item = ""
				for item in group:
					pass
				
				context['jsmulist2'].append([item.result.race.date, item.mu])
				
			context['len_js1'] = len(context['jsmulist1'])
			context['len_js2'] = len(context['jsmulist2'])
			
			# calculate win probability
			# TODO: add list of races where they have competed against each other
			fscore1 = context['rscores1'].latest('result__race__date')
			fscore2 = context['rscores2'].latest('result__race__date')
			context['fscore1'] = fscore1
			context['fscore2'] = fscore2
			
			wp1 = 1 - norm.cdf( -(fscore1.mu - fscore2.mu) / (fscore1.sigma + fscore2.sigma) )
			wp2 = 1 - wp1
			
			context['win_prob1'] = wp1 * 100
			context['win_prob2'] = wp2 * 100
			
			context['error'] = 0
			
		except ObjectDoesNotExist:
			# no scores for one of the rowers
			context['error'] = 1
	except ObjectDoesNotExist:
		# a rower is missing
		context['error'] = 2
	
	return render(request, 'rowing/rower_compare.html', context)
	
class RaceList(ListView):
	model = Race
	paginate_by = 30
	ordering = ['name']
	
'''class RaceDetail(DetailView):
	model = Race'''
	
def RaceDetail(request, pk):
	race = Race.objects.get(pk=pk)
	results = Result.objects.filter(race__id=pk).order_by('position')
	
	context = {'object':race, 'results':results}
	
	return render(request, 'rowing/race_detail.html', context)
	
# in progress
# Want /races to go to list of competitions
# Want /races/1 to go to list of all Races for that competition, with filters by event
class CompetitionList(ListView):
	model = Competition
	paginate_by = 30
	ordering = ['name']
	
class ClubList(ListView):
	model = Club
	paginate_by = 50
	ordering = ['name']	
	
class ClubDetail(DetailView):
	model = Club
	
def Compare(request):

	if request.method == 'POST':
		form = CompareForm(request.POST)
		if form.is_valid():
			surl = '/compare/' + str(form.cleaned_data['rower1'].pk) + '/' + str(form.cleaned_data['rower2'].pk) + '/?type=' + str(form.cleaned_data['type'])
			return HttpResponseRedirect(surl)
	
	else:
		form = CompareForm()
		return render(request, 'rowing/compare.html', {'form':form})

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
'''
class RankingList(ListView):
	queryset = Rower.objects.all()
	template_name = 'test'
	ordering = ['sweep_mu']
'''	
def RankingView(request):
	# to add on get parameter for scull/sweep
	#ptype = "Sweep"
	ptype = request.GET.get('type','Sweep')
	g = request.GET.get('g', 'M')
	
	'''
	# filter to ensure there is a minimum no of scores
	min_length = 4
	
	# filter to ensure recency of result
	cutoff_date = datetime.date(2016, 7, 5)
	
	rankings = []
	
	# gets the latest score for each rower
	for rower in Rower.objects.all():
		# perhaps put a try to skip rowers with no results
		s2 = rower.score_set.filter(result__race__event__type=ptype)
		
		# filter by latest provided they have sufficient results
		if len(s2) > min_length:
			s1 = s2.latest('result__race__date')
			# ensure the result is in the recent period
			if s1.result.race.date > cutoff_date:
				rankings.append({'name': rower.name, 'mu': s1.mu, 'id': rower.pk, 'sigma': s1.sigma, 'date': s1.result.race.date})
	
	# sort by mu, ie the second item in the sublist
	#rankings = rankings.sorted(rankings, key = lambda x: x[1], reverse=True)
	rankings = sorted(rankings, key = lambda x: (x['mu']-x['sigma']), reverse=True)
	
	# cutoff to top 50
	rankings = rankings[:50]
	'''
	
	rankings = ScoreRanking.objects.filter(type=ptype, rower__gender=g).order_by('-delta_mu_sigma')[:50]
	#t1 = rankings[0].type
	
	form = RankingForm(request.GET)
	
	return render(request, 'rowing/ranking.html', {'rankings': rankings, 'type': ptype, 'gender': g, 'form': form})