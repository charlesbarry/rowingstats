# script to import the 2018 bucs regatta data

#TODO: move to django management command, allow options such as rollback for events

from rowing.models import Rower, Race, Result, Club, Competition, Event, Time
import json, csv, datetime, logging, os, pickle
from django.db.models import Q
from scripts.raceimporter import crewsearch, clubsearch, add_time

##### BEGIN CONFIG #####
logging.basicConfig(filename='./log/metlog.log', level=logging.INFO, format='%(levelname)s: %(message)s')
logging.info("####### Start of Log ########")
logging.info("Timestamp -- %s", datetime.datetime.strftime(datetime.datetime.now(), "%H:%M:%S - %A, %d %B %Y"))

SATDATE = datetime.date(2018, 5, 5)
SUNDATE = datetime.date(2018, 5, 6)
MONDATE = datetime.date(2018, 5, 7)

basedir = '../met/2019 Regatta/'

met = Competition.objects.get(pk=9)

# composite placeholder is 362 on production, 188 on local (laptop), 50 on local (desktop)
composite_placeholder = Club.objects.get(pk=362)

##### END CONFIG #####
	
logging.info("Config and preparatory tasks completed.")

##### CREATION OF EVENTS AND RACES ######
fname = basedir + 'event_list.csv'
with open(fname, 'r', encoding='UTF-8-sig', newline='') as csvfile:
	reader = csv.reader(csvfile)
	eventdata = (list(reader))
	
	logging.info("Event data successfully loaded. Starting create_events()")
	print("Starting to create events...")
	
for ev in eventdata:
	try:
		Event.objects.get(name = ev[0])
	except Event.DoesNotExist:
		try:
			if "x" in ev[0]:
				type = 'Sculling'
			else:
				type = 'Sweep'
		
			new_event = Event.objects.create(
					name = ev[0],
					comp = met,
					type = type,
					distance = '2000m',
				)
			logging.debug("Event created with parameters as follows - name=%s, type=%s", ev[0], type)
		except Exception as e:
			logging.error("Exception incurred for Event %s: %s", ev[0], str(e))
			raise e
		
logging.info("All events added to DB.")
print("All events added to DB.")
##### END RACE/EVENT CREATION #####

logging.info("####### End of Log ########")	