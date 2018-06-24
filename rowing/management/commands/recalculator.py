# custom command to recalculate scores based on data

from django.core.management.base import BaseCommand, CommandError
from rowing.models import Result, Rower, Race, Score, Event, ScoreRanking
from trueskill import Rating, rate, setup
from django.db import transaction
from itertools import groupby
import datetime

DEFAULT_SIGMA = 10.0 # Used to be (25/3)
DEFAULT_MU = 0.0 # 100.0
INT_MU = 10.0 # 110.0

setup(beta=5, tau=0.5, draw_probability=0.002)

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
			if rgroups[i][j].mu < 0.0:
				tmu = 0.0
			else:
				tmu = rgroups[i][j].mu
			Score.objects.create(
				mu = rgroups[i][j].mu,
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
		)
	
@transaction.atomic
def reset_scores():
	# double_check what happens with on delete in models
	Score.objects.all().delete()
	ScoreRanking.objects.all().delete()
	
class Command(BaseCommand):
	help = 'Recalculates the scores of rowers'

	'''def add_arguments(self, parser):
		parser.add_argument('poll_id', nargs='+', type=int)'''

	def handle(self, *args, **options):
		# clear all previous scores, reset to default
		error = 0
		reset_scores()
		print("Scores reset to default.")
		
		races_used = Race.objects.filter(complete = True)
		
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
					if len(trial) > 0:
						temp.append(
							Rating(mu=trial.latest("result__race__date").mu,
							sigma=trial.latest("result__race__date").sigma)
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
		print("Beginning ranking calculations.")
		
		#cutoff_date = datetime.date(2016, 7, 5)
		min_length = 4
		# gets the latest score for each rower
		for rower in Rower.objects.all():
			s2 = rower.score_set.all()
			# filter by latest provided they have sufficient results
			if len(s2) > min_length:
				s1 = s2.latest('result__race__date')
				# ensure the result is in the recent period
				#if s1.result.race.date > cutoff_date:
				add_ranking({'rower': rower, 'mu': s1.mu, 'sigma': s1.sigma, 'delta_mu_sigma': (s1.mu-s1.sigma), 		'date': s1.result.race.date, 'type': s1.result.race.event.type})
		
		print("Completed ranking calculations")	