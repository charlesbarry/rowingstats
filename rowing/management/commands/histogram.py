# custom command to output scores of every rower

from django.core.management.base import BaseCommand, CommandError
from rowing.models import Result, Rower, Race, Score, Event, ScoreRanking
from django.db.models import Avg

class Command(BaseCommand):
	help = 'Shows averages and other stats'

	'''def add_arguments(self, parser):
		parser.add_argument('poll_id', nargs='+', type=int)'''

	def handle(self, *args, **options):
		# get the latest scores
		rscores = []
		for rower in Rower.objects.all():
			try:
				s1 = rower.score_set.all().latest('result__race__date')
				rscores.append([s1.mu, s1.sigma])
			except:
				pass
		
		for item in rscores:
			print(item[0], ",", item[1])

			
		