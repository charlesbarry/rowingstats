# custom command to check that no rower exists in the same race

from django.core.management.base import BaseCommand, CommandError
from rowing.models import Result, Rower, Race, Score, Event, ScoreRanking
from trueskill import Rating, rate, setup
from django.db import transaction
from django.db.models import Avg
from itertools import groupby
import datetime

class Command(BaseCommand):
	help = 'Recalculates the scores of rowers'

	'''def add_arguments(self, parser):
		parser.add_argument('poll_id', nargs='+', type=int)'''

	def handle(self, *args, **options):
		duplicates = []
		unusuals = []
		iavgs = []
		for trace in Race.objects.all():
			checked = []
			for tresult in trace.result_set.all():
				for athlete in tresult.crew.all():
					if athlete in checked:
						duplicates.append([athlete.name, tresult.position, trace.name])
					else:
						checked.append(athlete)
					
				if tresult.crew.count() not in [1, 2, 4, 8]:
					unusuals.append([tresult.crew.count(), trace.name, tresult.clubs.all()[0].name])
					#print("Unusual crew number (%s) found in %s" % (trace.name, tresult.crew.count()))
		
		# check the average number of people in each crew
		check_avg = sum([item.crew.count() for item in trace.result_set.all()]) / trace.result_set.count()
		if check_avg not in [1, 2, 4, 8]:
			iavgs.append([check_avg, trace.name])
		
		if len(duplicates) > 0:
			print("The following duplicates were found:")
			for item in duplicates:
				print(item[0], " - ", item[1], " - ", item[2])
				
		else:
			print("No duplicates found")

		if len(unusuals) > 0:
			print("The following unusual crew numbers were found:")
			for item in unusuals:
				print(item[0], " - ", item[1], " - ", item[2])
				
		else:
			print("No unusual crew numbers found")
			
		if len(iavgs) > 0:
			print("The following inconsistent averages were found:")
			for item in iavgs:
				print(item[1], " - Average: ", item[0])
		else:
			print("No inconsistent averages found")
		