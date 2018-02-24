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
from django.utils import timezone

from django.views.generic import ListView, DetailView, UpdateView, TemplateView
from .models import Rower, Race, Result, Competition, Event, Score, Club, ScoreRanking
from .forms import CompareForm, RankingForm, RowerForm, CrewCompareForm, CompetitionForm
from django.views.decorators.csrf import csrf_exempt

def add_years(d, years):
	# stolen from stackoverflow: https://stackoverflow.com/a/15743908
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).

    """
    try:
        return d.replace(year = d.year + years)
    except ValueError:
        return d + (datetime.date(d.year + years, 1, 1) - datetime.date(d.year, 1, 1))

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
	
def IndexView2(request):
	context = {}
	context['races'] = Race.objects.count()
	context['rowers'] = Rower.objects.count()
	context['results'] = Result.objects.count()

	return render(request, 'rowing/index2.html', context)
	
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
	ptype = request.GET.get('type')
	copyGET = request.GET.copy() # required because request.GET is otherwise immutable
	r1 = Rower.objects.get(pk=pk)
	
	if ptype in (None, ''):
		if r1.score_set.filter(result__race__event__type='Sweep').count() == 0:
			copyGET['type'] = 'Sculling'
			ptype = 'Sculling'
		else:
			copyGET['type'] = 'Sweep'
			ptype = 'Sweep'
	
	context['object'] = r1
	#context['jsuplist'] = []
	context['jsmulist']	= []
	#context['jslolist'] = []
	context['jscilist'] = []
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
			
			#context['jsuplist'].append([item2.result.race.date, (item2.mu+item2.sigma)])
			context['jsmulist'].append([item2.result.race.date, item2.mu])
			#context['jslolist'].append([item2.result.race.date, (item2.mu-item2.sigma)])
			context['jscilist'].append([item2.result.race.date, (item2.mu-item2.sigma), (item2.mu+item2.sigma)])
		
	except ObjectDoesNotExist:
		context['scores'] = None
	#context['clubs'] = r1.result_set.all()
	
	context['form'] = RowerForm(copyGET)
	
	return render(request, 'rowing/rower_detail.html', context)
	
@csrf_exempt
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
	
def RowerCompare2(request):
	ptype = request.GET.get('type','Sweep')
	pk1 = request.GET.get('rower1', None)
	pk2 = request.GET.get('rower2', None)
	context = {}
	context['type'] = ptype
	context['jsmulist1'] = []
	context['jsmulist2'] = []
	
	if pk1 is not None and pk2 is not None:
	# render the comparison
	
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
			# a rower is missing from the db
			context['error'] = 2
	
	else:
		# if a rower is missing from the get string
		context['error'] = 3
		
		# serve up the blank page
	
	context['form'] = CompareForm(request.GET)
	
	return render(request, 'rowing/rower_compare2.html', context)	

def CrewCompare(request):
	ptype = request.GET.get('type','Sweep')
	crewpk1 = request.GET.get('crew1', None)
	crewpk2 = request.GET.get('crew2', None)
	context = {}
	context['type'] = ptype
	
	if crewpk1 is not None and crewpk2 is not None:
		# parse the pks (from |26|27| to ['26','27'])
		crewpk1 = crewpk1[1:-1].split('|')
		crewpk2 = crewpk2[1:-1].split('|')
	
		# render the comparison	
		rowers1 = []
		rowers2 = []
		for member in crewpk1:
			r1 = Rower.objects.get(pk=member)
			try:
				r1s = r1.score_set.filter(result__race__event__type=ptype).order_by('result__race__date', 'result__race__order').latest('result__race__date')
				rowers1.append([r1,r1s.mu,r1s.sigma, r1s.result.race.date])
			except ObjectDoesNotExist:
				rowers1.append([r1,100.0,10.0, 'No data (default assumed)'])
			
		for member in crewpk2:
			r1 = Rower.objects.get(pk=member)
			try:
				r2 = r1.score_set.filter(result__race__event__type=ptype).order_by('result__race__date', 'result__race__order').latest('result__race__date')
				rowers2.append([r1,r2.mu,r2.sigma, r2.result.race.date])
			except ObjectDoesNotExist:
				rowers2.append([r1,100.0,10.0, 'No data (default assumed)'])
				
		context['rowers1'] = rowers1
		context['rowers2'] = rowers2
		
		# calculate the win probability
		mu1 = 0
		sigma1 = 0
		mu2 = 0
		sigma2 = 0
		
		for r in rowers1:
			mu1 += r[1]
			sigma1 += r[2]
			
		for r in rowers2:
			mu2 += r[1]
			sigma2 += r[2]
		
		wp1 = 1 - norm.cdf( -(mu1 - mu2) / (sigma1 + sigma2) )
		wp2 = 1 - wp1
		
		context['mu1'] = mu1
		context['sigma1'] = sigma1
		context['mu2'] = mu2
		context['sigma2'] = sigma2
		context['win_prob1'] = wp1 * 100
		context['win_prob2'] = wp2 * 100
	
		context['error'] = 0 # clean pass
	else:
		# if a rower is missing from the get string
		# serve up the blank page
		context['error'] = 1
		
	context['form'] = CrewCompareForm(request.GET)
	
	return render(request, 'rowing/crew_compare.html', context)	
	
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
'''class CompetitionList(ListView):
	model = Competition
	paginate_by = 30
	ordering = ['name']'''
	
def CompetitionView(request):
	data = Competition.objects.all().order_by('name')
	
	return render(request, 'rowing/competition.html', {'data':data})
	
def CompetitionResults(request, pk):
	rtype = request.GET.get('type')
	#gender = request.GET.get('g') - to be implemented (data not in model)
	event = request.GET.get('event')
	raceclass = request.GET.get('raceclass')
	year = request.GET.get('year') #- to be implemented
	context = {}
	context['competition'] = Competition.objects.get(pk=pk)
	
	races = Race.objects.filter(event__comp__pk=pk)
	# add a filter for year
	if event not in (None, ''):
		races = races.filter(event=event)
	if rtype not in (None, ''):
		races = races.filter(event__type=rtype)
	if raceclass not in (None, ''):
		races = races.filter(raceclass=raceclass)
		
	# pre_year_races exists so that the year_choices filter ignores the current year
	# if this didn't exist, selecting a year would remove the other years from the form choices
	pre_year_races = races
	if year not in (None, ''):
		races = races.filter(date__year=year)
	
	
	context['races'] = races.order_by('-date')
	
	# adds the count for the entries
	for item in context['races']:
		item.total_pos = Result.objects.filter(race__id=item.pk).count()
	
	# create event and class choices for form and create the form
	raceclass_choices = [('','Any')]
	for item in context['races'].order_by('raceclass').values_list('raceclass', flat=True).distinct():
		raceclass_choices.append((item,item))
	
	event_choices = [('','Any')]
	for item3 in context['races'].order_by('event__name').values_list('event',flat=True).distinct():
		event_choices.append((item3, Event.objects.get(pk=item3).name))
	
	# NB different method for dates
	year_choices = [('', 'Any')]
	for yitem in pre_year_races.dates('date', 'year', order='DESC'):
		year_choices.append((yitem.year, yitem.year))
	
	context['form'] = CompetitionForm(raceclass_choices, event_choices, year_choices, request.GET)
	
	return render(request, 'rowing/competition_results.html', context)
	
class ClubList(ListView):
	model = Club
	paginate_by = 50
	ordering = ['name']	
	
def ClubDetail(request, pk):
	this_club = Club.objects.get(pk=pk)
	
	#TODO: filtering by year, with a form and everything
	#this_year = request.GET.get('year', timezone.now().year)
	
	# work out people who raced for that club in that year - set avoids duplicates
	temp_members = set()
	for this_result in this_club.result_set.all():
		for this_rower in this_result.crew.all():
			temp_members.add(this_rower)
	
	# turn the set into a sorted list	
	club_members = sorted(temp_members, key = lambda x: x.name, reverse=False)
	
	# work out races the club took part in that year
	temp_races = set()
	for this_result in this_club.result_set.all():
		temp_races.add(this_result.race)
		
	club_races = sorted(temp_races, key = lambda x: x.name, reverse=False)
	
	# creates the entry total
	for item in club_races:
		item.total_pos = Result.objects.filter(race__id=item.pk).count()
		
	context = {'club': this_club, 'races': club_races, 'members': club_members}
	return render(request, 'rowing/club_detail.html', context)
	
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
	currentrank = request.GET.get('current','y')
	gbonly = request.GET.get('gb','y')
	
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
	#t1 = rankings[0].type
		# get ranking based on type and gender
	rankings = ScoreRanking.objects.filter(type=ptype, rower__gender=g).order_by('-delta_mu_sigma')
	'''
	
	tmp_currentdate = add_years(datetime.date.today(), -1)
	
	if currentrank == "y":
		if gbonly == "y":
			rankings = ScoreRanking.objects.filter(type=ptype, rower__gender=g, date__gte=tmp_currentdate, rower__nationality='GBR').order_by('-delta_mu_sigma')[:50]
		else:
			rankings = ScoreRanking.objects.filter(type=ptype, rower__gender=g, date__gte=tmp_currentdate).order_by('-delta_mu_sigma')[:50]
	else:
		if gbonly == "y":
			rankings = ScoreRanking.objects.filter(type=ptype, rower__gender=g, rower__nationality='GBR').order_by('-delta_mu_sigma')[:50]
		else:
			rankings = ScoreRanking.objects.filter(type=ptype, rower__gender=g).order_by('-delta_mu_sigma')[:50]
	
	form = RankingForm(request.GET)
	
	return render(request, 'rowing/ranking.html', {'rankings': rankings, 'type': ptype, 'gender': g, 'form': form})