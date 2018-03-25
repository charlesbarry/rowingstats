# custom command to calculate averages of the scores

from django.core.management.base import BaseCommand, CommandError
from rowing.models import Result, Rower, Race, Score, Event, ScoreRanking
from django.db.models import Avg

class Command(BaseCommand):
	help = 'Shows averages and other stats'

	'''def add_arguments(self, parser):
		parser.add_argument('poll_id', nargs='+', type=int)'''

	def handle(self, *args, **options):
		# part 1: averages of everyone in the ScoreRanking list
		sr_mu = ScoreRanking.objects.all().aggregate(Avg('mu'))
		sr_sigma = ScoreRanking.objects.all().aggregate(Avg('sigma'))
		
		print("Averages of ranked rowers:")
		print("Average mu:", sr_mu)
		print("Average sigma:", sr_sigma)
		
		# part 2: averages of all rowers' latest scores
		# get the latest scores
		rscores = []
		for rower in Rower.objects.all():
			try:
				s1 = rower.score_set.all().latest('result__race__date')
				rscores.append([s1.mu, s1.sigma])
			except:
				pass
		
		# work out the averages by summing and dividing
		s_mu = 0
		s_sigma = 0
		for item in rscores:
			s_mu += item[0]
			s_sigma += item[1]
		
		print("Of all rowers (including unranked:")
		print("Average mu:", s_mu / len(rscores))
		print("Average sigma:", s_sigma / len(rscores))
			
		