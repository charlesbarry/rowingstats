# custom command to check that no rower exists in the same race

from django.core.management.base import BaseCommand, CommandError
from rowing.models import Result, Rower, Race, Score, Event, ScoreRanking
from trueskill import Rating, rate, setup
from django.db import transaction
from django.db.models import Avg
from itertools import groupby
import datetime, logging

logging.basicConfig(filename='./log/rowercheck.log', level=logging.DEBUG, format='%(levelname)s: %(message)s')
logging.info("##### START OF LOG ######")
logging.info("Timestamp -- %s", datetime.datetime.strftime(datetime.datetime.now(), "%H:%M:%S - %A, %d %B %Y"))

class Command(BaseCommand):
	help = 'Recalculates the scores of rowers'

	'''def add_arguments(self, parser):
		parser.add_argument('poll_id', nargs='+', type=int)'''

	def handle(self, *args, **options):
		duplicates = []
		unusuals = []
		iavgs = []
		for trace in Race.objects.all():
			checked = set()
			for tresult in trace.result_set.all():
				for athlete in tresult.crew.all():
					if athlete in checked:
						try:
							duplicates.append([athlete.name, tresult.position, trace.name])
						except IndexError:
							logging.error("IndexError incurred for attempt to add %s, %s and %s to duplicates", athlete.name, tresult.position, trace.name)
					else:
						checked.add(athlete)
					
				if tresult.crew.count() not in [1, 2, 4, 8]:
					try:
						unusuals.append([tresult.crew.count(), trace.name, tresult.clubs.all()[0].name])
					except IndexError:
						logging.error("IndexError incurred for %s - appears no clubs in result", tresult.crew.count(), trace.name)
					#print("Unusual crew number (%s) found in %s" % (trace.name, tresult.crew.count()))
		
		# check the average number of people in each crew
		try:
			check_avg = sum([item.crew.count() for item in trace.result_set.all()]) / trace.result_set.count()
			if check_avg not in [1, 2, 4, 8]:
				iavgs.append([check_avg, trace.name])
		except ZeroDivisionError:
			logging.error("ZeroDivisionError incurred for %s - appears no results", trace.name)
		
		if len(duplicates) > 0:
			print("The following duplicates were found:")
			for item in duplicates:
				print(item[0], " - ", item[1], " - ", item[2])
				logging.error("Duplicate found: name=%s, race=%s, position=%s", item[0], item[2], item[1])
				
		else:
			print("No duplicates found")
			logging.info("No duplicates found")

		if len(unusuals) > 0:
			print("The following unusual crew numbers were found:")
			for item in unusuals:
				print(item[0], " - ", item[1], " - ", item[2])
				logging.error("Unusual crew number found: race=%s, club=%s, crewsize=%s", item[1], item[2], item[0])
				
		else:
			print("No unusual crew numbers found")
			logging.info("No duplicates found")
			
		if len(iavgs) > 0:
			print("The following inconsistent averages were found:")
			for item in iavgs:
				print(item[1], " - Average: ", item[0])
				logging.error("Inconsistent average found: race=%s, average=%s", item[1], str(item[0]))
		else:
			print("No inconsistent averages found")
			logging.info("No inconsistent averages")

		logging.info("##### END OF LOG ######")