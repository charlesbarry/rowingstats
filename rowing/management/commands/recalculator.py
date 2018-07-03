# custom command to recalculate scores based on data

from django.core.management.base import BaseCommand, CommandError
from rowing.models import Result, Rower, Race, Score, Event, ScoreRanking
from trueskill import Rating, rate, setup
from django.db import transaction
from itertools import groupby
import datetime, logging

logging.basicConfig(filename='./log/recalculator.log', level=logging.INFO, format='%(levelname)s: %(message)s')
logging.info("Timestamp -- %s", datetime.datetime.strftime(datetime.datetime.now(), "%H:%M:%S - %A, %d %B %Y"))

DEFAULT_SIGMA = 10 # Used to be (25/3)
DEFAULT_MU = 0.0 # 100.0
INT_MU = 10.0 # 110.0
BETA = 10
TAU = 0.5
DRAW_PROB = 0.002
DTA = True # dynamic tau on or off
DFLOOR = True

DYNAMIC_TAU_ADJUSTMENT = 730

setup(beta=BETA, tau=TAU, draw_probability=DRAW_PROB)

logging.info("Recalculator being run with parameters: default sigma=%s, default mu=%s, international mu=%s, dynamic tau period (days)=%s, beta=%s, tau=%s, draw	probability=%s, dynamic tau=%s, score floor=%s", DEFAULT_SIGMA, DEFAULT_MU, INT_MU, DYNAMIC_TAU_ADJUSTMENT, BETA, TAU, DRAW_PROB, DTA, DFLOOR)

#changes that need to be made
# 1) DONE - change reset to wipe all saved scores
# 2) DONE - change update to insert into the scores table
# 3) DONE - change extraction algo to get latest member of the score table for that rower
# 4) DONE - import type from Event not Race
# 3 is probably Score.objects.filter(rower_id=rower_id).latest()
# put a try statement

@transaction.atomic
def update_ts(n, rgroups, type):
	for i, item in enumerate(Result.objects.filter(race_id = n).order_by('position')):
		for j, member in enumerate(item.crew.all()):
			# score floor at 0
			if rgroups[i][j].mu < 0.0 and DFLOOR == True:
				tmu = 0.0
			else:
				tmu = rgroups[i][j].mu
			Score.objects.create(
				mu = tmu,
				sigma = rgroups[i][j].sigma,
				#race = item.race,
				result = item,
				rower = member,
				)
				
@transaction.atomic
def add_ranking(data):
	ScoreRanking.objects.create(
		mu = data['mu'],
		sigma = data['sigma'],
		delta_mu_sigma = data['delta_mu_sigma'],
		rower = data['rower'],
		date = data['date'],
		type = data['type'],
		sr_type = data['sr_type'],
		)
	
class Command(BaseCommand):
	help = 'Recalculates the scores of rowers'

	def add_arguments(self, parser):
		parser.add_argument('--date', action='store', help='Starts calculations from YYYY-MM-DD')
		parser.add_argument('--sr', action='store_true', help='Only recalculate ScoreRankings')

	def handle(self, *args, **options):
		# skip if sr option active
		if not options['sr']:
			# handle custom start date
			if options['date']:
				#shorten this bloody variable
				od = options['date']
				# parse the date
				rday = int(od[od.rfind('-')+1:])
				rmonth = int(od[od.find('-')+1:od.rfind('-')])
				ryear = int(od[:od.find('-')])
				
				rdate = datetime.date(ryear, rmonth, rday)
			
				#delete everything AFTER this date
				Score.objects.filter(result__race__date__gte=rdate).delete()
				
				
				# use only races AFTER this date
				races_used = Race.objects.filter(complete = True, date__gte=rdate)
			
			else:
				Score.objects.all().delete()
				races_used = Race.objects.filter(complete = True)
			
			error = 0
			print("Scores reset to default.")
			logging.info("Total races being calculated on: %s", races_used.count())
			
			# loop through all complete races
			counter = 0
			length = len(races_used)
			for race_i in races_used.order_by('date','order'):
				ratings = []
				positions = []
				error_list = []
				r_error = 0
				# loop through every result in that race to create the ratings figure
				for item in Result.objects.filter(race_id = race_i.pk).order_by('position'):
					# loop through every crew member, and extract their scores
					temp = []
					mu_sum = 0
					for member in item.crew.all():
						trial = member.score_set.filter(result__race__event__type=race_i.event.type)		
						if trial.count() > 0:
							dsigma = trial.latest("result__race__date").sigma

							# dynamic tau
							if dsigma < DEFAULT_SIGMA and trial.count() > 1 and DTA == True:
								d1 = trial.order_by("-result__race__date")[0].result.race.date
								d2 = trial.order_by("-result__race__date")[1].result.race.date
								ddiff = d1 - d2
								dsigma += ((DEFAULT_SIGMA - dsigma) * min(DYNAMIC_TAU_ADJUSTMENT, ddiff.days)/DYNAMIC_TAU_ADJUSTMENT)
							
							temp.append(
								Rating(mu=trial.latest("result__race__date").mu,
								sigma=dsigma)
								)
							mu_sum += trial.latest("result__race__date").mu
						elif race_i.raceclass == "International":
							temp.append(
								Rating(mu=INT_MU,
								sigma=DEFAULT_SIGMA)
							)
							mu_sum += INT_MU
						else:
							temp.append(
								Rating(mu=DEFAULT_MU,
								sigma=DEFAULT_SIGMA)
							)
							mu_sum += DEFAULT_MU
					ratings.append(temp)
				
					# create the positions list
					positions.append(item.position)
					
					error_list.append([mu_sum, item.position])
				
				# create the expected result by ranking the crews on their prior score - also avoids ties
				# appends the rank on the end of the error_list entry
				sorted_error_list = sorted(error_list, reverse=True)
				exp_rank = 0
				for _, grp in groupby(sorted_error_list, key = lambda y: y[0]):
					r = exp_rank + 1
					for x in grp:
						x.append(r)
						exp_rank += 1
						
				# calculate the error in the event		
				for item in error_list:
					r_error += ((item[1]-item[2])**2)
				
				try:
					r_error = r_error / len(error_list)
				except:
					print("Error! Race %s has no results!" % race_i.name)
					continue
				
				# run the TrueSkill algorithm
				try:
					rgroups = rate(ratings, ranks=positions)
				except:
					print("Error! Race %s has only 1 entry!" % race_i.name)
					continue
				
				#update the rower scores with the outcomes - looping through results and rowers
				'''for i, item in enumerate(Result.objects.filter(race_id = race_i.pk).order_by('position')):
					for j, member in enumerate(item.crew.all()):
						if race_i.type == "Sweep":
							member.mu_sweep = rgroups[i][j].mu
							member.sigma_sweep = rgroups[i][j].sigma
						elif race_i.type == "Sculling":
							member.mu_scull = rgroups[i][j].mu
							member.sigma_scull = rgroups[i][j].sigma
						member.save()'''
						
				#alt update method
				update_ts(race_i.pk, rgroups, race_i.event.type)
				
				#show progress
				counter += 1
				count_progress = round((counter/length)*100, 1)
				error += r_error
				print("Race %s completed. (%s).\t Race error: %s \t (%s)" % (race_i.pk, str(count_progress)+"%", str(round(r_error,2)), race_i.name))
				
			print("Calculations completed. Total error was %s" % (str(round(error,2))))
			logging.info("Total error was %s", str(round(error,2)))
		print("Beginning ranking calculations.")
		logging.info("Beginning ranking calculations - resetting ScoreRankings")
		
		# delete all ScoreRankings
		ScoreRanking.objects.all().delete()
		
		# gets the latest score for each rower
		for rower in Rower.objects.all():
			s2 = rower.score_set.all()
			# requires to have more than 5 results
			if s2.count() > 4:
				s1 = s2.latest('result__race__date')
				s_max = s2.extra(select={'dsm':'mu - sigma'}).order_by('-dsm')[0]
				# ensure the result is in the recent period
				#if s1.result.race.date > cutoff_date:
				add_ranking({'rower': rower, 'mu': s1.mu, 'sigma': s1.sigma, 'delta_mu_sigma': (s1.mu-s1.sigma), 		'date': s1.result.race.date, 'type': s1.result.race.event.type, 'sr_type': 'Current'})
				add_ranking({'rower': rower, 'mu': s_max.mu, 'sigma': s_max.sigma, 'delta_mu_sigma': s_max.dsm, 		'date': s_max.result.race.date, 'type': s_max.result.race.event.type, 'sr_type': 'All time'})
		
		print("Completed ranking calculations")