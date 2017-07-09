# custom command to check that no rower exists in the same race

from django.core.management.base import BaseCommand, CommandError
from rowing.models import Result, Rower, Race, Score, Event, ScoreRanking
from trueskill import Rating, rate, setup
from django.db import transaction
from itertools import groupby
import datetime

class Command(BaseCommand):
	help = 'Recalculates the scores of rowers'

	'''def add_arguments(self, parser):
		parser.add_argument('poll_id', nargs='+', type=int)'''

	def handle(self, *args, **options):
		duplicates = []
		unusuals = []
		for trace in Race.objects.all():
			checked = []
			for tresult in trace.result_set.all():
				for athlete in tresult.crew.all():
					if athlete in checked:
						duplicates.append([athlete.name, tresult.position, trace.name])
					else:
						checked.append(athlete)
					
				if tresult.crew.count() not in [1, 2, 4, 8]:
					unusuals.append([tresult.crew.count(), trace.name])
					#print("Unusual crew number (%s) found in %s" % (trace.name, tresult.crew.count()))
		
		if len(duplicates) > 0:
			print("The following duplicates were found:")
			for item in duplicates:
				print(item[0], " - ", item[1], " - ", item[2])
				
		else:
			print("No duplicates found")

		if len(unusuals) > 0:
			print("The following unusual crew numbers were found:")
			for item in unusuals:
				print(item[0], " - ", item[1])
				
		else:
			print("No unusual crew numbers found")
		