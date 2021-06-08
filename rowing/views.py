from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
import datetime, os, requests, json
from django.core.management import call_command
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from itertools import groupby
from scipy.stats import norm
from django.utils import timezone
from django.db.models import Max, Min
from django.contrib import messages
from django.core import serializers

from django.views.generic import ListView, DetailView, UpdateView, TemplateView
from .models import Rower, Race, Result, Competition, Event, Score, Club, ScoreRanking, Time, Fixture, KnockoutRace, CumlProb, Edition, ProposedChange
from .forms import CompareForm, RankingForm, RowerForm, RowerCorrectForm, CrewCompareForm, CompetitionForm, FixtureEditionForm, FixtureEventForm, RowerMergeForm, ResultCorrectForm
from django.views.decorators.csrf import csrf_exempt

### helper functions
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

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

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
    # TODO: refactor so all results are shown (across all six types)
    
    context = {}
    ptype = request.GET.get('type')
    copyGET = request.GET.copy() # required because request.GET is otherwise immutable
    try:
        r1 = Rower.objects.get(pk=pk)
    except Rower.DoesNotExist:
        raise Http404('Rower not found')
    
    if ptype in (None, ''):
        if r1.score_set.filter(result__race__event__type='Sweep').count() == 0:
            copyGET['type'] = 'Sculling'
            ptype = 'Sculling'
        else:
            copyGET['type'] = 'Sweep'
            ptype = 'Sweep'
    
    context['object'] = r1
    #context['jsuplist'] = []
    context['jsmulist']    = []
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
            
            # floor function to prevent lower confidence interval going below zero
            if (item2.mu-item2.sigma) < 0.0:
                lci = 0.0
            else:
                lci = (item2.mu-item2.sigma)
            context['jscilist'].append([item2.result.race.date, lci, (item2.mu+item2.sigma)])
        
    except ObjectDoesNotExist:
        context['scores'] = None
    
    #context['clubs'] = r1.result_set.all()
    
    context['form'] = RowerForm(copyGET)
    
    # generates the 'ranked Nth of X'
    tdt = add_years(datetime.date.today(), -1)
    # Event.type_choices is ((dbname, prettyname),)
    context['rower_ranks'] = []
    for type in Event.type_choices:
        try:
            csr = r1.scoreranking_set.get(sr_type='Current', type=type[0])
        except ScoreRanking.DoesNotExist:
            continue
        
        ranked_ahead_nat = ScoreRanking.objects.filter(delta_mu_sigma__gt=csr.delta_mu_sigma, type=type[0], sr_type='Current', date__gte=tdt, rower__gender=r1.gender, rower__nationality=r1.nationality).count()

        total_ranked_nat = ScoreRanking.objects.filter(type=type[0], sr_type='Current', date__gte=tdt, rower__gender=r1.gender, rower__nationality=r1.nationality).count()
        
        ranked_ahead_all = ScoreRanking.objects.filter(delta_mu_sigma__gt=csr.delta_mu_sigma, type=type[0], sr_type='Current', date__gte=tdt, rower__gender=r1.gender).count()

        total_ranked_all = ScoreRanking.objects.filter(type=type[0], sr_type='Current', date__gte=tdt, rower__gender=r1.gender).count()
        
        context['rower_ranks'].append((type[1], ranked_ahead_nat, total_ranked_nat, ranked_ahead_all, total_ranked_all))
    
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
                rowers1.append([r1,0.0,10.0, 'No data (default assumed)'])
            
        for member in crewpk2:
            r1 = Rower.objects.get(pk=member)
            try:
                r2 = r1.score_set.filter(result__race__event__type=ptype).order_by('result__race__date', 'result__race__order').latest('result__race__date')
                rowers2.append([r1,r2.mu,r2.sigma, r2.result.race.date])
            except ObjectDoesNotExist:
                rowers2.append([r1,0.0,10.0, 'No data (default assumed)'])
                
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
    try:
        race = Race.objects.get(pk=pk)
    except Race.DoesNotExist:
        raise Http404('Race not found')
    results = Result.objects.filter(race__id=pk).order_by('position')
    if Time.objects.filter(result__race__id=pk).count() > 0:
        time_flag = True
    else:
        time_flag = False
        
    
    context = {'object':race, 'results':results, 'time_flag': time_flag}
    
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
    year = request.GET.get('year')
    page = request.GET.get('page')
    context = {}
    try:
        context['competition'] = Competition.objects.get(pk=pk)
    except Competition.DoesNotExist:
        raise Http404('No such competition exists')
    
    races = Race.objects.filter(event__comp__pk=pk, complete=True)
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
    
    # rather than calling races to the context directly, call via paginator
    # this prevents the page hanging while 1000+ races are requested and iterated!
    races_list = races.order_by('-date')
    paginator = Paginator(races_list, 100)
    context['races'] = paginator.get_page(page)
    
    # get the editions
    context['editions'] = Edition.objects.filter(comp_id=pk)
    
    # adds the count for the entries
    for item in context['races']:
        item.total_pos = Result.objects.filter(race__id=item.pk).count()
    
    # create event and class choices for form and create the form
    raceclass_choices = [('','Any')]
    for item in races_list.order_by('raceclass').values_list('raceclass', flat=True).distinct():
        raceclass_choices.append((item,item))
    
    event_choices = [('','Any')]
    for item3 in races_list.order_by('event__name').values_list('event',flat=True).distinct():
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
    
def EditionDetail(request, pk):
    try:
        edition = Edition.objects.get(pk=pk)
    except Edition.DoesNotExist:
        raise Http404('No such edition exists')
    fixtures = edition.fixture_set.all()
    context = {'edition':edition, 'fixtures':fixtures}

    return render(request, 'rowing/edition_detail.html', context)
    
def FixtureDetail(request, pk):
    try:
        fixture = Fixture.objects.get(pk=pk)
    except Fixture.DoesNotExist:
        raise Http404('No such fixture exists')
    races = fixture.race_set.all()
    racelinks = fixture.racelink_set.all()
    context = {'fixture':fixture, 'races':races, 'racelinks':racelinks}
    
    edition_choices = [(x.pk, x.edition.name) for x in fixture.event.fixture_set.all()]
    context['editionform'] = FixtureEditionForm(edition_choices, request.GET)
    
    event_choices = [(x.pk, x.event.name) for x in fixture.edition.fixture_set.all()]
    context['eventform'] = FixtureEventForm(event_choices, request.GET)
    
    # stupid workaround for django forms inability to make init work properly
    context['init_edition'] = fixture.pk
    context['init_event'] = fixture.pk
    
    if races.count() > 0:
        rmax = races.aggregate(Max('round'))['round__max']
        rmin = races.aggregate(Min('round'))['round__min']
        # due to zero indexing have to add the +1 to the max
        context['columns'] = [races.filter(round=x).order_by('slot') for x in range(rmin,rmax+1)]

    return render(request, 'rowing/fixture_detail.html', context)
    
def ClubDetail(request, pk):
    try:
        this_club = Club.objects.get(pk=pk)
    except Club.DoesNotExist:
        raise Http404('No such club exists')
    
    #TODO: filtering by year, with a form and everything
    #this_year = request.GET.get('year', timezone.now().year)
    #TODO: pagination
    
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
        
    club_races = sorted(temp_races, key = lambda x: x.date, reverse=True)
    
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
    
    # take today minus one year as the cutoff for current scores
    tmp_currentdate = add_years(datetime.date.today(), -1)
    
    if currentrank == "y":
        if gbonly == "y":
            rankings = ScoreRanking.objects.filter(type=ptype, rower__gender=g, date__gte=tmp_currentdate, rower__nationality='GBR', sr_type='Current').order_by('-delta_mu_sigma')[:50]
        else:
            rankings = ScoreRanking.objects.filter(type=ptype, rower__gender=g, date__gte=tmp_currentdate, sr_type='Current').order_by('-delta_mu_sigma')[:50]
    else:
        if gbonly == "y":
            rankings = ScoreRanking.objects.filter(type=ptype, rower__gender=g, rower__nationality='GBR', sr_type='All time').order_by('-delta_mu_sigma')[:50]
        else:
            rankings = ScoreRanking.objects.filter(type=ptype, rower__gender=g, sr_type='All time').order_by('-delta_mu_sigma')[:50]
    
    form = RankingForm(request.GET)
    
    return render(request, 'rowing/ranking.html', {'rankings': rankings, 'type': ptype, 'gender': g, 'form': form})
    
def KnockoutView(request, pk):
    try:
        knockout = Fixture.objects.get(pk=pk)
    except Fixture.DoesNotExist:
        raise Http404('Fixture not found')
    context = {'knockout':knockout}
    context['rdayn'] = request.GET.get('day', 'Wednesday')
    kraces = KnockoutRace.objects.filter(knockout=knockout)
    # weirdly produces a single item dictionary with round__max as key
    # rounds = kraces.aggregate(Max('round'))['round__max']
    # TODO add a column 0 which is just the crews pre race
    context['columns'] = []
    
    # COMMENT: Is this still needed? (Not touching for now as it works)
    for r in range(1, knockout.rounds+1):
        rowspan = (2*r - 1)
        context['columns'].append((rowspan, kraces.filter(round=r).order_by('slot')))
    
    # annotate the first column with offset slot n for template rendering convenience
    for krace in context['columns'][0][1]:
        # TODO insert match probability
        krace.slotz = (krace.slot-1)
            
    context['cumlprobs'] = CumlProb.objects.filter(knockout=knockout, dayn=context['rdayn']).exclude(cumlprob=0).order_by('-cumlprob')
    # crewname__startswith='Bye-',
    for c in context['cumlprobs']:
        c.prob = str(round(c.cumlprob*100, 2)) + '%'
        # render the odds...
        '''
        if c.cumlprob == 0:
            c.odds = '0'
        elif c.cumlprob > 0.5:
            todds = 1/((1/c.cumlprob)-1)
            c.odds = str(round(todds, 1)) + ' : 1' 
        else:
            todds = (1/c.cumlprob)-1
            c.odds = '1 : ' + str(round(todds, 1)) '''
    
    return render(request, 'rowing/knockoutdetail.html', context)
    
### CORRECTION VIEWS ###

def RowerCorrect(request, pk):
    try:
        rower = Rower.objects.get(pk=pk)
    except Rower.DoesNotExist:
        raise Http404('Rower not found')
    
    if request.method == 'POST':
        form = RowerCorrectForm(request.POST)
        if form.is_valid():
            # reCAPTCHA validation
            rdata = {
                'secret': os.environ.get("RECAPTCHA_PRIVATE_KEY"),
                'response': request.POST.get('g-recaptcha-response'),
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=rdata)
            result = r.json()
            
            if result['success']:
                # trim the form.cleaned_data to exclude the non-submitter elements
                data_to_check = {k: form.cleaned_data[k] for k in form.cleaned_data.keys() & {'name', 'nationality', 'gender'}}
                # filter out unchanged fields
                changes = {k:data_to_check[k] for k in data_to_check if data_to_check[k] != getattr(rower, k)}
                
                # check number of changes is > 0, if so crack on
                if len(changes) != 0:
                    ProposedChange.objects.create(
                        submitter_name = form.cleaned_data['your_name'],
                        submitter_email = form.cleaned_data['your_email'],
                        submitted_ip = get_client_ip(request),
                        model = 'Rower',
                        model_pk = rower.pk,
                        # comprehension to extract subset of dict - from https://stackoverflow.com/questions/5352546
                        data = json.dumps(changes),
                        operation = 'update',
                    )
                    messages.success(request, "Your changes were received. They'll now be reviewed by a site admin before being approved.")
                    return redirect('rower-detail', pk=rower.pk)
                else:
                    messages.error(request, "You don't appear to have submitted any changes.")
            else:
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
            
    
    else:
        form = RowerCorrectForm(initial={'gender':rower.gender, 'nationality':rower.nationality, 'name':rower.name})

    return render(request, 'rowing/rower_correct.html', {'rower':rower, 'form':form})

def RowerMerge(request, pk):
    try:
        rower = Rower.objects.get(pk=pk)
    except Rower.DoesNotExist:
        raise Http404('Rower not found')
    
    if request.method == 'POST':
        form = RowerMergeForm(request.POST)
        if form.is_valid():
            # reCAPTCHA validation
            rdata = {
                'secret': os.environ.get("RECAPTCHA_PRIVATE_KEY"),
                'response': request.POST.get('g-recaptcha-response'),
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=rdata)
            result = r.json()
            
            if result['success']:
                if form.cleaned_data['merger'] != rower:
                    ProposedChange.objects.create(
                        submitter_name = form.cleaned_data['your_name'],
                        submitter_email = form.cleaned_data['your_email'],
                        submitted_ip = get_client_ip(request),
                        model = 'Rower',
                        model_pk = rower.pk,
                        data = json.dumps({'merge_from':rower.pk, 'merge_into':form.cleaned_data['merger'].pk}),
                        operation = 'merge',
                    )
                    messages.success(request, "Your changes were received. They'll now be reviewed by a site admin before being approved.")
                    return redirect('rower-detail', pk=rower.pk)
                else:
                    messages.error(request, "You don't appear to have submitted any changes.")
            else:
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
            
    
    else:
        form = RowerMergeForm()

    return render(request, 'rowing/rower_merge.html', {'rower':rower, 'form':form})     
    
def ResultCorrect(request, pk):
    try:
        res = Result.objects.get(pk=pk)
    except Result.DoesNotExist:
        raise Http404('Rower not found')
    
    if request.method == 'POST':
        form = ResultCorrectForm(request.POST)
        if form.is_valid():
            # reCAPTCHA validation
            rdata = {
                'secret': os.environ.get("RECAPTCHA_PRIVATE_KEY"),
                'response': request.POST.get('g-recaptcha-response'),
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=rdata)
            result = r.json()
            
            if result['success']:
                # trim the form.cleaned_data to exclude the non-submitter elements
                data_to_check = {k: form.cleaned_data[k] for k in form.cleaned_data.keys() & {'cox','flag','crews','clubs'}}
                # filter out unchanged fields
                changes = {k:data_to_check[k] for k in data_to_check if data_to_check[k] != getattr(res, k)}
                # slightly hackish workaround to deal with M2M fields
                '''if form.cleaned_data['crew'] != [str(x.pk) for x in res.crew.all()]:
                    changes['crew'] = form.cleaned_data['crew']
                    
                if form.cleaned_data['clubs'] != [str(x.pk) for x in res.clubs.all()]:
                    changes['clubs'] = form.cleaned_data['crew']'''
                    
                # hackish workaround for the fact that django matches foreign key fields as the object itself
                if 'cox' in changes:
                    changes['cox'] = changes['cox'].pk
                
                if len(changes) != 0:
                    ProposedChange.objects.create(
                        submitter_name = form.cleaned_data['your_name'],
                        submitter_email = form.cleaned_data['your_email'],
                        submitted_ip = get_client_ip(request),
                        model = 'Result',
                        model_pk = res.pk,
                        data = json.dumps(changes),
                        operation = 'update',
                    )
                    
                    messages.success(request, "Your changes were received. They'll now be reviewed by a site admin before being approved.")
                    messages.debug(request, form.cleaned_data)
                    return redirect('race-detail', pk=res.race.pk)
                else:
                    messages.error(request, "You don't appear to have submitted any changes.")
            else:
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
            
    #'crew','clubs','cox','flag' initial={'crew':rower.gender, 'nationality':rower.nationality, 'name':rower.name}
    else:
        form = ResultCorrectForm(initial={'crew':res.crew.all(), 'clubs':res.clubs.all(), 'cox':res.cox, 'flag':res.flag})

    return render(request, 'rowing/result_correct.html', {'result':res, 'form':form})