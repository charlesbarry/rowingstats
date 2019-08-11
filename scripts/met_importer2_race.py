# script to import the 2018 bucs regatta data

#TODO: move to django management command, allow options such as rollback for events

from rowing.models import Rower, Race, Result, Club, Competition, Event, Time
import json, csv, datetime, logging, os
from django.db.models import Q

##### BEGIN CONFIG #####
logging.basicConfig(filename='./log/metlog.log', level=logging.INFO, format='%(levelname)s: %(message)s')
logging.info("####### Start of Log ########")
logging.info("Timestamp -- %s", datetime.datetime.strftime(datetime.datetime.now(), "%H:%M:%S - %A, %d %B %Y"))

SATDATE = datetime.date(2019, 6, 1)
SUNDATE = datetime.date(2019, 6, 2)
MONDATE = datetime.date(2019, 6, 3)

basedir = '../met/2019 Regatta/sat/'

met = Competition.objects.get(pk=9)

# composite placeholder is 362 on production, 188 on local (laptop), 50 on local (desktop)
composite_placeholder = Club.objects.get(pk=362)


composite = False
##### END CONFIG #####

logging.info("Config and preparatory tasks completed.")

##### CREATION OF EVENTS AND RACES ######
fname = basedir + 'race_list.json'
with open(fname) as jsonfile:
	jdata = json.load(jsonfile)
	racedata = jdata['data']

logging.info("Race data successfully loaded. Starting createraces()")
print("Starting to create races...")

for race in racedata:
	#remove html artifacts
	if "&" in race['Round']:
		race['Round'] = race['Round'][:race['Round'].find("&")]
	
	rname = (race['FullName'] + " - " + race['Round'])
	
	if race['Day'] == "Saturday":
		rdate = SATDATE
	elif race['Day'] == "Sunday":
		rdate = SUNDATE
	elif race['Day'] == "Monday":
		rdate = MONDATE
	
	try:
		Race.objects.get(name = rname, date = rdate, rnumber = int(race['Race']))
		logging.debug("Skipping race %s as already in the DB - number %s on %s.", rname, race['Race'], rdate)
	except Race.DoesNotExist:	
		if 'Heat' or 'TT' in race['Round']:
			order = 0
		elif 'Rep' in race['Round'] or 'Semi' in race['Round']:
			order = 1
		elif 'Final' in race['Round']:
			order = 2
		
		logging.debug("Trying to add %s to the DB - Event %s.", rname, race['Event'])
		try:
			new_race = Race.objects.create(
					name = rname,
					date = rdate,
					raceclass = "Open",
					event = Event.objects.get(name=race['Event']),
					order = order,
					rnumber = int(race['Race']),
					complete = False,				
				)
		except Event.DoesNotExist:
			if "x" in race['Event']:
				type = 'Sculling'
			else:
				type = 'Sweep'
		
			new_event = Event.objects.create(
					name = race['Event'],
					comp = met,
					type = type,
					distance = '2000m',
				)
			logging.debug("Event created with parameters as follows - name=%s, type=%s", ev[0], type)
			new_race = Race.objects.create(
					name = rname,
					date = rdate,
					raceclass = "Open",
					event = Event.objects.get(name=race['Event']),
					order = order,
					rnumber = int(race['Race']),
					complete = False,				
				)
		except Exception as e:
			logging.error("Exception incurred for Race %s: %s", rname, str(e))
			raise e	
		logging.info("Race %s added to DB." % rname)

logging.info("All races added to DB.")
print("All races added to DB.")


##### END RACE/EVENT CREATION #####
logging.info("####### End of Log ########")	