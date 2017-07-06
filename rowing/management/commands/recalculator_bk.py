# custom command to recalculate scores based on data

from django.core.management.base import BaseCommand, CommandError
from rowing.models import Result, Rower, Race
from trueskill import Rating, rate, setup
from django.db import transaction

DEFAULT_SIGMA = (25/3)
DEFAULT_MU = 100.0

#changes that need to be made
# 1) change reset to wipe all saved scores
# 2) change update to insert into the scores table
# 3) change extraction algo to get latest member of the score table for that rower
# 3 is probably Score.objects.filter(rower_id=rower_id).latest()
# put a try statement

@transaction.atomic
def update_ts(n, rgroups, type):
	for i, item in enumerate(Result.objects.filter(race_id = n).order_by('position')):
		for j, member in enumerate(item.crew.all()):
			if type == "Sweep":
				member.mu_sweep = rgroups[i][j].mu
				member.sigma_sweep = rgroups[i][j].sigma
			elif type == "Sculling":
				member.mu_scull = rgroups[i][j].mu
				member.sigma_scull = rgroups[i][j].sigma
			member.save()
	
@transaction.atomic
def reset_scores():
	'''for rower in Rower.objects.all():
		rower.mu_scull = DEFAULT_MU
		rower.mu_sweep = DEFAULT_MU
		rower.sigma_scull = DEFAULT_SIGMA
		rower.sigma_sweep = DEFAULT_SIGMA
		rower.save()'''
	
class Command(BaseCommand):
	help = 'Recalculates the scores of rowers'

	'''def add_arguments(self, parser):
		parser.add_argument('poll_id', nargs='+', type=int)'''

	def handle(self, *args, **options):
		# clear all previous scores, reset to default
		reset_scores()
		print("Scores reset to default.")
		
		# loop through all races
		counter = 0
		length = len(Race.objects.all())
		for race_i in Race.objects.order_by('date'):
			ratings = []
			positions = []
			# loop through every result in that race to create the ratings figure
			for item in Result.objects.filter(race_id = race_i.pk).order_by('position'):
				# loop through every crew member, and extract their scores
				temp = []
				for member in item.crew.all():
					if race_i.type == "Sweep":
						temp.append(Rating(mu=member.mu_sweep,sigma=member.sigma_sweep))
					elif race_i.type == "Sculling":
						temp.append(Rating(mu=member.mu_scull,sigma=member.sigma_scull))
				ratings.append(temp)
			
				# create the positions list
				positions.append(item.position)
			
			# run the TrueSkill algorithm
			rgroups = rate(ratings, ranks=positions)
			
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
			update_ts(race_i.pk, rgroups, race_i.type)
			
			#show progress
			counter += 1
			count_progress = round((counter/length)*100, 1)
			print("Race %s completed. (%s)" % (race_i.pk, str(count_progress)+"%"))
			